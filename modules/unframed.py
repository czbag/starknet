import random

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import UNFRAMED_CONTRACT, UNFRAMED_ABI


class Unframed(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

    @retry
    @check_gas("starknet")
    async def cancel_order(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Unframed cancel order")

        random_nonce = random.randint(
            296313738189912513306030367211954909183182558840765666364410788857347237284,
            3618502788666131213697322783095070105623107215331596699973092056135872020480
        )

        contract = self.get_contract(UNFRAMED_CONTRACT, UNFRAMED_ABI, 1)

        unframed_call = contract.functions["cancel_orders"].prepare(order_nonces=[random_nonce])

        transaction = await self.sign_transaction([unframed_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
