from loguru import logger
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from web3 import Web3

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from config import ZKLEND_CONTRACT, ZKLEND_ETH_CONCTRACT, STARKNET_TOKENS


class ZkLend(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

    async def get_deposit_amount(self):
        zklend_eth_contract = self.get_contract(ZKLEND_ETH_CONCTRACT)

        amount_data = await zklend_eth_contract.functions["balanceOf"].call(
            self.address
        )
        amount = amount_data.balance

        return amount

    @retry
    @check_gas
    async def deposit(
            self,
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
        amount_wei, amount, balance = await self.get_amount(
            "ETH",
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{hex(self.address)}] Make deposit on ZkLend")

        approve_contract = self.get_contract(STARKNET_TOKENS["ETH"])

        approve_call = approve_contract.functions["approve"].prepare(
            ZKLEND_CONTRACT,
            amount_wei
        )

        deposit_call = Call(
            to_addr=ZKLEND_CONTRACT,
            selector=get_selector_from_name("deposit"),
            calldata=[STARKNET_TOKENS["ETH"], amount_wei],
        )

        transaction = await self.sign_transaction([approve_call, deposit_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

        if make_withdraw:
            sleep(sleep_from, sleep_to)

            await self.withdraw_all()

    @retry
    @check_gas
    async def withdraw_all(self):
        amount = await self.get_deposit_amount()

        logger.info(
            f"[{self._id}][{hex(self.address)}] Make withdraw from ZkLend | " +
            f"{Web3.from_wei(amount, 'ether')} ETH"
        )

        if amount > 0:
            withdraw_all_call = Call(
                to_addr=ZKLEND_CONTRACT,
                selector=get_selector_from_name("withdraw_all"),
                calldata=[STARKNET_TOKENS["ETH"]],
            )

            transaction = await self.sign_transaction([withdraw_all_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.error(f"[{self._id}][{hex(self.address)}] Deposit not found")

    @retry
    @check_gas
    async def enable_collateral(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Make enable collateral on ZkLend")

        enable_collateral_call = Call(
            to_addr=ZKLEND_CONTRACT,
            selector=get_selector_from_name("enable_collateral"),
            calldata=[STARKNET_TOKENS["ETH"]],
        )

        transaction = await self.sign_transaction([enable_collateral_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

    @retry
    @check_gas
    async def disable_collateral(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Make disable collateral on ZkLend")

        disable_collateral_call = Call(
            to_addr=ZKLEND_CONTRACT,
            selector=get_selector_from_name("disable_collateral"),
            calldata=[STARKNET_TOKENS["ETH"]],
        )

        transaction = await self.sign_transaction([disable_collateral_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
