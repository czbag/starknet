import random

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from config import STARKGUARDIANS_CONTRACT, STARKGUARDIANS_ABI


class StarkGuardians(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.contract = self.get_contract(STARKGUARDIANS_CONTRACT, STARKGUARDIANS_ABI)

    @staticmethod
    def get_random_name():
        token_name = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(7, 15)))
        token_symbol = token_name.upper()[0:random.randint(3, 5)]

        return token_name, token_symbol

    @retry
    @check_gas("starknet")
    async def deploy_token(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Deploy token contract")

        token_name, token_symbol = self.get_random_name()

        deploy_call = self.contract.functions["deployContract"].prepare(
            0x0339d10811d97e91d1343d2faa7fac3116e9714f99b59617705070ada6f5a05a,
            random.randint(38890058876971531151, 85735143683896744799),
            1,
            [
                token_name,
                token_symbol,
                self.address,
                random.randint(1000000000000000000000, 10000000000000000000000000000)
            ]
        )

        transaction = await self.sign_transaction([deploy_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

    @retry
    @check_gas("starknet")
    async def deploy_nft(self, sleep_from: int, sleep_to: int):
        logger.info(f"[{self._id}][{hex(self.address)}] Deploy NFT contract")

        token_name, token_symbol = self.get_random_name()

        deploy_call = self.contract.functions["deployContract"].prepare(
            0x745c9a10e7bc32095554c895490cfaac6c4c8cada2e3763faddedfaa72c856a,
            random.randint(38890058876971531151, 85735143683896744799),
            1,
            [
                token_name,
                token_symbol,
                self.address,
            ]
        )

        transaction = await self.sign_transaction([deploy_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

        await sleep(sleep_from, sleep_to)

        await self.mint_nft(transaction_response.transaction_hash)

    @retry
    @check_gas("starknet")
    async def mint_nft(self, tx_hash: int):
        logger.info(f"[{self._id}][{hex(self.address)}] Mint NFT")

        data = await self.get_transaction(tx_hash)

        contract = self.get_contract(data.events[0].from_address, STARKGUARDIANS_ABI)

        mint_call = contract.functions["mint"].prepare(self.address)

        transaction = await self.sign_transaction([mint_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
