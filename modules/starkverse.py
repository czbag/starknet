from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import STARKVERSE_CONTRACT, STARKVERSE_ABI


class Starkverse(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(STARKVERSE_CONTRACT, STARKVERSE_ABI)

    @retry
    @check_gas("starknet")
    async def mint(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Mint Starkverse NFT")

        mint_call = self.contract.functions["publicMint"].prepare(self.address)

        transaction = await self.sign_transaction([mint_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
