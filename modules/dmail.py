import random
from hashlib import sha256

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import DMAIL_CONTRACT, DMAIL_ABI


class Dmail(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(DMAIL_CONTRACT, DMAIL_ABI)

    @retry
    @check_gas("starknet")
    async def send_mail(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Dmail send mail")

        email_address = sha256(str(1e10 * random.random()).encode()).hexdigest()
        theme = sha256(str(1e10 * random.random()).encode()).hexdigest()

        dmail_call = self.contract.functions["transaction"].prepare(email_address[0:31], theme[0:31])

        transaction = await self.sign_transaction([dmail_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
