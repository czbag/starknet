import random
from typing import List

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from config import STARKNET_TOKENS, STARKSTARS_ABI


class StarkStars(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

    @retry
    @check_gas("starknet")
    async def mint(
            self,
            contracts: List,
            quantity_mint_min: int,
            quantity_mint_max,
            mint_all: bool,
            sleep_from: int,
            sleep_to: int
    ):
        approve_contract = self.get_contract(STARKNET_TOKENS["ETH"])

        quantity_mint = random.randint(quantity_mint_min, quantity_mint_max)

        contracts = contracts if mint_all is True else random.sample(contracts, quantity_mint)

        logger.info(f"[{self._id}][{hex(self.address)}] Mint {quantity_mint} StarkStars NFT")

        for _, contract in enumerate(contracts, start=1):
            nft_contract = self.get_contract(contract, STARKSTARS_ABI, 1)

            (mint_price, ) = await nft_contract.functions["get_price"].call()
            (nft_id, ) = await nft_contract.functions["name"].call()

            nft_name = bytearray.fromhex(hex(nft_id)[2:]).decode()

            logger.info(f"[{self._id}][{hex(self.address)}] Mint #{nft_name} NFT")

            approve_call = approve_contract.functions["approve"].prepare(
                contract,
                mint_price
            )

            mint_starkstars_call = nft_contract.functions["mint"].prepare()

            transaction = await self.sign_transaction([approve_call, mint_starkstars_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)

            if _ == len(contracts):
                await sleep(sleep_from, sleep_to)
