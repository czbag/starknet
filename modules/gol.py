from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import GOL2_CONTRACT, GOL2_ABI


class Gol(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(GOL2_CONTRACT, GOL2_ABI)

    @retry
    @check_gas("starknet")
    async def mint_token(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Mint Gol token")

        mint_call = self.contract.functions["evolve"].prepare(39132555273291485155644251043342963441664)

        transaction = await self.sign_transaction([mint_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
