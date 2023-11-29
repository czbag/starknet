from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import ALMANAC_CONTRACT, ALMANAC_ABI


class Almanac(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(ALMANAC_CONTRACT, ALMANAC_ABI)

    @retry
    @check_gas("starknet")
    async def approve_nft(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Make Almanac approve")

        approve_call = self.contract.functions["setApprovalForAll"].prepare(
            0x7d4dc2bf13ede97b9e458dc401d4ff6dd386a02049de879ebe637af8299f91d,
            1
        )

        transaction = await self.sign_transaction([approve_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
