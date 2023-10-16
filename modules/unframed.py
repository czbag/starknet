import random
from string import hexdigits

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

        random_nonce = "0x" + "".join(random.choice(hexdigits[:-6]) for _ in range(63))

        contract = self.get_contract(UNFRAMED_CONTRACT, UNFRAMED_ABI, 1)

        unframed_call = contract.functions["cancel_orders"].prepare(order_nonces=random_nonce)

        transaction = await self.sign_transaction([unframed_call], 1)

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
