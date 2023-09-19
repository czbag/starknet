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
            "fibrous": Fibrous
        }

    def get_swap_module(self, use_dex: list):
        swap_module = random.choice(use_dex)

        return self.swap_modules[swap_module]

    async def swap(
            self,
            use_dex: list,
            sleep_from: int,
            sleep_to: int,
            min_swap: int,
            max_swap: int,
            slippage: int,
            random_swap_token: bool,
            min_percent: int,
            max_percent: int
    ):
        quantity_swap = random.randint(min_swap, max_swap)

        if random_swap_token:
            balance = await self.get_balance(STARKNET_TOKENS["USDC"])
            path = [random.choice(["ETH", "USDC"]) for _ in range(0, quantity_swap)]
            if path[0] == "USDC" and balance["balance"] <= 1:
                path[0] = "ETH"
        else:
            path = ["ETH" if _ % 2 == 0 else "USDC" for _ in range(0, quantity_swap)]

        logger.info(f"[{self._id}][{hex(self.address)}] Start MultiSwap | quantity swaps: {quantity_swap}")

        for _, token in enumerate(path, start=1):
            if token == "ETH":
                decimal = 6
                to_token = "USDC"

                balance = await self.account.get_balance()

                min_amount = float(Web3.from_wei(int(balance / 100 * min_percent), "ether"))
                max_amount = float(Web3.from_wei(int(balance / 100 * max_percent), "ether"))
            else:
                decimal = 18
                to_token = "ETH"

                balance = await self.get_balance(STARKNET_TOKENS["USDC"])

                min_amount = balance["balance"] if balance["balance"] <= 1 else balance["balance"] / 100 * min_percent
                max_amount = balance["balance"] if balance["balance"] <= 1 else balance["balance"] / 100 * max_percent

            swap_module = self.get_swap_module(use_dex)(self._id, self.private_key, self.type_account)
            await swap_module.swap(
                token,
                to_token,
                min_amount,
                max_amount,
                decimal,
                slippage,
                False,
                min_percent,
                max_percent
            )

            if _ != len(path):
                sleep(sleep_from, sleep_to)
