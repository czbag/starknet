import random

from loguru import logger

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Account
from config import BRIDGE_CONTRACTS, DEPOSIT_ABI, RPC


class Bridge(Account):

    def __init__(self, _id: int, private_key: str, type_account: str, recipient: str) -> None:
        super().__init__(_id, private_key, recipient)

        self.type_account = type_account
        self.client = FullNodeClient(random.choice(RPC["starknet"]["rpc"]))

    async def get_l2_gas(self, amount: int):
        estimate_fee = await self.client.estimate_message_fee(
            from_address="0xae0ee0a63a2ce6baeeffe56e7714fb4efe48d419",
            to_address="0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
            entry_point_selector=get_selector_from_name("handle_deposit"),
            payload=[
                self.address,
                amount,
                0
            ]
        )

        return estimate_fee.overall_fee

    async def get_tx_data(self, value: int):
        tx = {
            "chainId": await self.w3.eth.chain_id,
            "from": self.address,
            "value": value,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
        }

        return tx

    @retry
    @check_gas("ethereum")
    async def deposit(
            self,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        amount_wei, amount, balance = await self.get_amount(
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{self.address}] Bridge to Starknet | {amount} ETH")

        gas_l2 = await self.get_l2_gas(amount_wei)

        tx_data = await self.get_tx_data(amount_wei + gas_l2)

        contract = self.get_contract(BRIDGE_CONTRACTS["deposit"], DEPOSIT_ABI)

        transaction = await contract.functions.deposit(
            amount_wei,
            int(self.recipient, 16)
        ).build_transaction(tx_data)

        signed_txn = await self.sign(transaction)

        txn_hash = await self.send_raw_transaction(signed_txn)

        await self.wait_until_tx_finished(txn_hash)
