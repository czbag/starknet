import asyncio
import time
import random

from starknet_py.net.gateway_client import GatewayClient

from web3 import Web3
from config import RPC
from settings import CHECK_GWEI, MAX_GWEI
from loguru import logger

from utils.sleeping import sleep


def get_gas():
    try:
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC["ethereum"]["rpc"])))
        gas_price = w3.eth.gas_price
        gwei = w3.from_wei(gas_price, 'gwei')
        return gwei
    except Exception as error:
        logger.error(error)


def wait_gas_ethereum():
    logger.info("Get GWEI")
    while True:
        gas = get_gas()

        if gas > MAX_GWEI:
            logger.info(f'Current GWEI: {gas} > {MAX_GWEI}')
            sleep(60, 70)
        else:
            logger.success(f"GWEI is normal | current: {gas} < {MAX_GWEI}")
            break


async def wait_gas_starknet():
    logger.info("Get GWEI")

    client = GatewayClient("mainnet")

    while True:
        block_data = await client.get_block("latest")
        gas = Web3.from_wei(block_data.gas_price, "gwei")

        if gas > MAX_GWEI:
            logger.info(f'Current GWEI: {gas} > {MAX_GWEI}')
            sleep(60, 70)
        else:
            logger.success(f"GWEI is normal | current: {gas} < {MAX_GWEI}")
            break


def check_gas(network: str):
    def decorator(func):
        def _wrapper(*args, **kwargs):
            if CHECK_GWEI:
                if network == "ethereum":
                    wait_gas_ethereum()
                else:
                    asyncio.create_task(wait_gas_starknet())
            return func(*args, **kwargs)

        return _wrapper

    return decorator
