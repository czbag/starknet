from loguru import logger

from config import MYSWAP_CONTRACT, MYSWAP_ABI, STARKNET_TOKENS
from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet


class MySwap(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(MYSWAP_CONTRACT, MYSWAP_ABI)

        self.pool_data = {
            "ETHUSDC": 1,
            "DAIETH": 2,
            "ETHUSDT": 4,
            "USDCUSDT": 5,
            "DAIUSDC": 6
        }

    async def get_pool_id(self, from_token: str, to_token: str):
        reverse = False

        pool_id = self.pool_data.get(from_token + to_token)
        if pool_id is None:
            reverse = True
            pool_id = self.pool_data.get(to_token + from_token)
            if pool_id is None:
                logger.error(f"Pool {from_token} <-> {to_token} not found ")
                return
        return pool_id, reverse

    async def get_min_amount_out(self, pool_id: int, reverse: bool, amount: int, slippage: float):
        (pool_data,) = await self.contract.functions["get_pool"].prepare(
            pool_id
        ).call()

        if reverse:
            reserveIn = pool_data.get("token_b_reserves")
            reserveOut = pool_data.get("token_a_reserves")
        else:
            reserveIn = pool_data.get("token_a_reserves")
            reserveOut = pool_data.get("token_b_reserves")

        min_amount_out = reserveOut * amount / reserveIn

        return int(min_amount_out - (min_amount_out / 100 * slippage))

    @retry
    @check_gas("starknet")
    async def swap(
            self,
            from_token: str,
            to_token: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            slippage: float,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        amount_wei, amount, balance = await self.get_amount(
            from_token,
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(
            f"[{self._id}][{hex(self.address)}] Swap on MySwap - {from_token} -> {to_token} | {amount} {from_token}"
        )

        pool_id, reverse = await self.get_pool_id(from_token, to_token)

        min_amount_out = await self.get_min_amount_out(pool_id, reverse, amount_wei, slippage)

        approve_contract = self.get_contract(STARKNET_TOKENS[from_token])

        approve_call = approve_contract.functions["approve"].prepare(
            MYSWAP_CONTRACT,
            amount_wei
        )

        swap_call = self.contract.functions["swap"].prepare(
            pool_id,
            STARKNET_TOKENS[from_token],
            amount_wei,
            min_amount_out,
        )

        transaction = await self.sign_transaction([approve_call, swap_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
