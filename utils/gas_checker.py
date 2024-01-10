import time
import random

from starknet_py.net.full_node_client import FullNodeClient

from web3 import Web3
from web3.eth import AsyncEth
from config import RPC
from settings import CHECK_GWEI, MAX_GWEI
from loguru import logger

from utils.sleeping import sleep


async def get_gas():
    try:
        w3 = Web3(
            Web3.AsyncHTTPProvider(random.choice(RPC["ethereum"]["rpc"])),
            modules={"eth": (AsyncEth,)},
        )
        gas_price = await w3.eth.gas_price
        gwei = w3.from_wei(gas_price, 'gwei')
        return gwei
    except Exception as error:
        logger.error(error)


async def wait_gas_ethereum():
    logger.info("Get GWEI ETH")
    while True:
        gas = await get_gas()

        if gas > MAX_GWEI:
            logger.info(f'Current GWEI: {gas} > {MAX_GWEI}')
            await sleep(60, 70)
        else:
            logger.success(f"GWEI is normal | current: {gas} < {MAX_GWEI}")
            break


async def wait_gas_starknet():
    logger.info("Get GWEI STARK")

    client = FullNodeClient(node_url=random.choice(RPC["starknet"]["rpc"]))

    while True:
        block_data = await client.get_block("latest")
        gas = Web3.from_wei(block_data.l1_gas_price.price_in_wei, "gwei")

        if gas > MAX_GWEI:
            logger.info(f'Current GWEI: {gas} > {MAX_GWEI}')
            await sleep(60, 70)
        else:
            logger.success(f"GWEI is normal | current: {gas} < {MAX_GWEI}")
            break


def check_gas(network: str):
    def decorator(func):
        async def _wrapper(*args, **kwargs):
            if CHECK_GWEI:
                if network == "ethereum":
                    await wait_gas_ethereum()
                else:
                    await wait_gas_starknet()
            return await func(*args, **kwargs)

        return _wrapper

    return decorator
