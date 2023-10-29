import random
from typing import List, Union

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from config import ZKLEND_CONCTRACTS, STARKNET_TOKENS, ZKLEND_ABI


class ZkLend(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(ZKLEND_CONCTRACTS["router"], ZKLEND_ABI)

    async def get_deposit_amount(self, token: str):
        zklend_contract = self.get_contract(ZKLEND_CONCTRACTS[token])

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

        logger.info(f"[{self._id}][{hex(self.address)}] Make deposit {token} on ZkLend")

        approve_contract = self.get_contract(STARKNET_TOKENS[token])

        approve_call = approve_contract.functions["approve"].prepare(
            ZKLEND_CONCTRACTS["router"],
            amount_wei
        )

        deposit_call = self.contract.functions["deposit"].prepare(
            STARKNET_TOKENS[token],
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
            f"[{self._id}][{hex(self.address)}] Make withdraw {token} from ZkLend"
        )

        if amount > 0:
            withdraw_all_call = self.contract.functions["withdraw_all"].prepare(
                STARKNET_TOKENS[token]
            )

            transaction = await self.sign_transaction([withdraw_all_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.error(f"[{self._id}][{hex(self.address)}] Deposit not found")

    @retry
    @check_gas("starknet")
    async def enable_collateral(self, use_token: List):
        token = random.choice(use_token)

        logger.info(f"[{self._id}][{hex(self.address)}] Make enable collateral {token} for ZkLend")

        enable_collateral_call = self.contract.functions["enable_collateral"].prepare(
            STARKNET_TOKENS[token]
        )

        transaction = await self.sign_transaction([enable_collateral_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

    @retry
    @check_gas("starknet")
    async def disable_collateral(self, use_token: List):
        token = random.choice(use_token)

        logger.info(f"[{self._id}][{hex(self.address)}] Make disable collateral {token} for ZkLend")

        disable_collateral_call = self.contract.functions["disable_collateral"].prepare(
            STARKNET_TOKENS[token]
        )

        transaction = await self.sign_transaction([disable_collateral_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
