import random

from loguru import logger
from web3 import Web3
from config import STARKNET_TOKENS
from modules import *
from utils.sleeping import sleep


class Multiswap(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.private_key = private_key
        self.type_account = type_account
        self.swap_modules = {
            "jediswap": Jediswap,
            "myswap": MySwap,
            "10kswap": StarkSwap,
            "sithswap": SithSwap,
            "protoss": Protoss,
            "avnu": Avnu,
        }

    def get_swap_module(self, use_dex: list):
        swap_module = random.choice(use_dex)

        return self.swap_modules[swap_module]

    async def swap(
            self,
            use_dex: list,
            use_tokens: list,
            sleep_from: int,
            sleep_to: int,
            min_swap: int,
            max_swap: int,
            slippage: int,
            min_percent: int,
            max_percent: int
    ):
        quantity_swap = random.randint(min_swap, max_swap)

        logger.info(f"[{self._id}][{hex(self.address)}] Start MultiSwap | quantity swaps: {quantity_swap}")

        tokens_data = [
            balance["symbol"] for balance in
            [await self.get_balance(STARKNET_TOKENS[token]) for token in use_tokens]
            if balance["balance"] != 0
        ]

        for _ in range(quantity_swap):
            from_token = "ETH" if len(tokens_data) == 0 else random.choice(["ETH", *tokens_data])
            to_token = random.choice([token for token in ["ETH", *use_tokens] if token != from_token])

            swap_module = self.get_swap_module(use_dex)(self._id, self.private_key, self.type_account)
            await swap_module.swap(
                from_token,
                to_token,
                0,
                0,
                6,
                slippage,
                True,
                min_percent,
                max_percent
            )

            if _ != quantity_swap:
                await sleep(sleep_from, sleep_to)
