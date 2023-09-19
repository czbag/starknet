from loguru import logger

from config import STARKNET_TOKENS
from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet


class Transfer(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str, recipient: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.recipient = recipient

    @retry
    @check_gas
    async def transfer_eth(
            self,
            min_amount: float,
            max_amount: float,
            decimal: int,
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

        logger.info(f"[{self._id}][{hex(self.address)}] Make transfer to {self.recipient} | {amount} ETH")

        contract = self.get_contract(STARKNET_TOKENS["ETH"])

        transfer_call = contract.functions["transfer"].prepare(int(self.recipient, 16), amount_wei)

        transaction = await self.sign_transaction([transfer_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
