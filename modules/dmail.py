import random
from loguru import logger
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet
from config import DMAIL_CONTRACT


class Dmail(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

    @staticmethod
    async def generate_mail_data():
        domain_list = ["@gmail.com", "@dmail.ai"]

        domain_address = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(5, 10)))
        theme = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(10, 20)))

        return domain_address + random.choice(domain_list), theme

    @retry
    @check_gas
    async def send_mail(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Dmail send mail")

        email_address, theme = await self.generate_mail_data()

        dmail_call = Call(
            to_addr=DMAIL_CONTRACT,
            selector=get_selector_from_name("transaction"),
            calldata=[email_address, theme],
        )

        transaction = await self.sign_transaction([dmail_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
