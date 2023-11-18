import random
from typing import List, Union

from loguru import logger
from config import STARKNET_TOKENS
from modules import *
from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep


class SwapTokens(Starknet):
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

    @retry
    @check_gas("starknet")
    async def swap(
            self,
            use_dex: List,
            tokens: List,
            sleep_from: int,
            sleep_to: int,
            slippage: Union[int, float],
            min_percent: int,
            max_percent: int,
    ):
        random.shuffle(tokens)

        logger.info(f"[{self._id}][{hex(self.address)}] Start swap tokens")

        for _, token in enumerate(tokens, start=1):
            balance = await self.get_balance(STARKNET_TOKENS[token])

            if balance["balance_wei"] > 0:
                swap_module = self.get_swap_module(use_dex)(self._id, self.private_key, self.type_account)
                await swap_module.swap(
                    token,
                    "ETH",
                    balance["balance"],
                    balance["balance"],
                    balance["decimal"],
                    slippage,
                    True,
                    min_percent,
                    max_percent
                )

            if _ != len(STARKNET_TOKENS):
                await sleep(sleep_from, sleep_to)
