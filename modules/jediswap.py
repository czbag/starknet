import time

from loguru import logger

from config import JEDISWAP_CONTRACT, JEDISWAP_ABI, STARKNET_TOKENS
from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet


class Jediswap(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(JEDISWAP_CONTRACT, JEDISWAP_ABI)

    async def get_min_amount_out(self, amount: int, slippage: float, path: list):
        min_amount_out_data = await self.contract.functions["get_amounts_out"].prepare(
            amountIn=amount,
            path=path
        ).call()

        min_amount_out = min_amount_out_data.amounts

        return int(min_amount_out[1] - (min_amount_out[1] / 100 * slippage))

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
            f"[{self._id}][{hex(self.address)}] Swap on Jediswap - {from_token} -> {to_token} | {amount} {from_token}"
        )

        path = [STARKNET_TOKENS[from_token], STARKNET_TOKENS[to_token]]

        deadline = int(time.time()) + 1000000

        min_amount_out = await self.get_min_amount_out(amount_wei, slippage, path)

        approve_contract = self.get_contract(STARKNET_TOKENS[from_token])

        approve_call = approve_contract.functions["approve"].prepare(
            JEDISWAP_CONTRACT,
            amount_wei
        )

        swap_call = self.contract.functions["swap_exact_tokens_for_tokens"].prepare(
            amount_wei,
            min_amount_out,
            path,
            self.address,
            deadline
        )

        transaction = await self.sign_transaction([approve_call, swap_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
