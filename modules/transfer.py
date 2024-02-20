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
    @check_gas("starknet")
    async def transfer_eth(
            self,
            token: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        amount_wei, amount, balance = await self.get_amount(
            token,
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{hex(self.address)}] Make transfer to {self.recipient} | {amount} {token}")

        contract = self.get_contract(STARKNET_TOKENS[token])

        balance = await self.get_balance(STARKNET_TOKENS[token])

        if amount_wei <= balance["balance_wei"]:
            transfer_call = contract.functions["transfer"].prepare(int(self.recipient, 16), amount_wei)

            fee = await transfer_call.estimate_fee()

            transfer_call = contract.functions["transfer"].prepare(int(self.recipient, 16), amount_wei - int(fee.overall_fee * 1.5))

            transaction = await self.sign_transaction([transfer_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.error(
                f"[{self._id}][{hex(self.address)}] Don't have money for transfer | balance: {balance['balance_wei']}"
            )
