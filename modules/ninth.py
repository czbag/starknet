from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import NINTH_CONTRACT, NINTH_ABI


class Ninth(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(NINTH_CONTRACT, NINTH_ABI, cairo_version=1)

    @retry
    @check_gas("starknet")
    async def approve_token(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Make Ninth approve")

        approve_call = self.contract.functions["approve"].prepare(
            0x274a2ef0e6aadb781777954ec78832fbe490de0f0f1484354b99f328f74ab36,
            20
        )

        transaction = await self.sign_transaction([approve_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
