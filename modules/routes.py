import random

from loguru import logger
from utils.sleeping import sleep
from . import Starknet


class Routes(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)

        self.private_key = private_key
        self.type_account = type_account

    async def start(self, use_modules: list, sleep_from: int, sleep_to: int, random_module: bool):
        logger.info(f"[{self._id}][{hex(self.address)}] Start using routes")

        for _ in range(0, len(use_modules)):
            if random_module:
                module = random.choice(use_modules)

                use_modules.remove(module)
            else:
                module = use_modules[_]

            module = random.choice(module) if type(module) is list else module

            await module(self._id, self.private_key, self.type_account)

            sleep(sleep_from, sleep_to)
