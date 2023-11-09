import asyncio

from loguru import logger
from tabulate import tabulate

from . import Starknet

from config import ACCOUNTS


async def get_nonce(account: Starknet):
    try:
        nonce = await account.account.get_nonce()

        return nonce
    except:
        await get_nonce(account)


async def check_tx(type_account: str):
    tasks = []

    logger.info("Start transaction checker")

    for _id, pk in enumerate(ACCOUNTS, start=1):
        account = Starknet(_id, pk, type_account)

        tasks.append(asyncio.create_task(get_nonce(account), name=hex(account.address)))

    await asyncio.gather(*tasks)

    table = [[k, i.get_name(), i.result()] for k, i in enumerate(tasks, start=1)]

    headers = ["#", "Address", "Nonce"]

    print(tabulate(table, headers, tablefmt="github"))
