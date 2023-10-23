import random
from typing import List, Union

from loguru import logger
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from config import NOSTRA_CONTRACTS, NOSTRA_ABI, STARKNET_TOKENS


class Nostra(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

    async def get_deposit_amount(self, token: str):
        zklend_contract = self.get_contract(NOSTRA_CONTRACTS[token])

        amount_data = await zklend_contract.functions["balanceOf"].call(
            self.address
        )
        amount = amount_data.balance

        return amount

    @retry
    @check_gas("starknet")
    async def deposit(
            self,
            use_token: List,
            min_amount: float,
            max_amount: float,
            decimal: int,
            sleep_from: int,
            sleep_to: int,
            make_withdraw: bool,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        token = random.choice(use_token)

        amount_wei, amount, balance = await self.get_amount(
            token,
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{hex(self.address)}] Make deposit {token} on Nostra")

        approve_contract = self.get_contract(STARKNET_TOKENS[token])

        approve_call = approve_contract.functions["approve"].prepare(
            NOSTRA_CONTRACTS[token],
            amount_wei
        )

        nostra_contract = self.get_contract(NOSTRA_CONTRACTS[token], NOSTRA_ABI)

        deposit_call = nostra_contract.functions["mint"].prepare(
            self.address,
            amount_wei
        )

        transaction = await self.sign_transaction([approve_call, deposit_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

        if make_withdraw:
            await sleep(sleep_from, sleep_to)

            await self.withdraw_all(token)

    @retry
    @check_gas("starknet")
    async def withdraw_all(self, use_token: Union[str, List]):
        token = random.choice(use_token) if type(use_token) is list else use_token

        amount = await self.get_deposit_amount(token)

        logger.info(
            f"[{self._id}][{hex(self.address)}] Make withdraw {token} from Nostra"
        )

        if amount > 0:
            nostra_contract = self.get_contract(NOSTRA_CONTRACTS[token], NOSTRA_ABI)

            withdraw_all_call = nostra_contract.functions["burn"].prepare(
                self.address,
                self.address,
                amount
            )

            transaction = await self.sign_transaction([withdraw_all_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.error(f"[{self._id}][{hex(self.address)}] Deposit not found")
