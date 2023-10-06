import aiohttp

from loguru import logger

from config import STARKNET_TOKENS, FIBROUS_CONTRACT, FIBROUS_ABI
from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet


async def get_route(from_token: int, to_token: int, amount: int):
    async with aiohttp.ClientSession() as session:
        url = "https://api.fibrous.finance/route"

        params = {
            "amount": hex(amount),
            "tokenInAddress": hex(from_token),
            "tokenOutAddress": hex(to_token),
            "excludeProtocols": 5
        }

        response = await session.get(url=url, params=params)
        response_data = await response.json()

        return response_data


class Fibrous(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

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
            f"[{self._id}][{hex(self.address)}] Swap on Fibrous - {from_token} -> {to_token} | {amount} {from_token}"
        )

        route = await get_route(STARKNET_TOKENS[from_token], STARKNET_TOKENS[to_token], amount_wei)

        min_amount_out = int(int(route["outputAmount"]) - (int(route["outputAmount"]) / 100 * slippage))

        contract = self.get_contract(FIBROUS_CONTRACT, FIBROUS_ABI)
        approve_contract = self.get_contract(STARKNET_TOKENS[from_token])

        approve_call = approve_contract.functions["approve"].prepare(
            FIBROUS_CONTRACT,
            amount_wei
        )

        swap_call = contract.functions["swap"].prepare(
            [{
                "token_in": STARKNET_TOKENS[from_token],
                "token_out": STARKNET_TOKENS[to_token],
                "rate": 1000000,
                "protocol": route["route"][0]["swaps"][0][0]["protocol"],
                "pool_address": int(route["route"][0]["swaps"][0][0]["poolAddress"], 16)
            }],
            {
                "token_in": STARKNET_TOKENS[from_token],
                "token_out": STARKNET_TOKENS[to_token],
                "amount": amount_wei,
                "min_received": min_amount_out,
                "destination": self.address
            }
        )

        transaction = await self.sign_transaction([approve_call, swap_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
