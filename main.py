import asyncio
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Union

import questionary
from loguru import logger
from questionary import Choice

from config import ACCOUNTS, RECIPIENTS
from utils.helpers import remove_wallet
from utils.sleeping import sleep
from modules_settings import *
from settings import (
    TYPE_WALLET,
    RANDOM_WALLET,
    SLEEP_FROM,
    SLEEP_TO,
    QUANTITY_THREADS,
    THREAD_SLEEP_FROM,
    THREAD_SLEEP_TO, REMOVE_WALLET
)


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Make deposit to Starknet", deposit_starknet),
            Choice("2) Make withdraw from Starknet", withdraw_starknet),
            Choice("3) Deploy argent account", deploy_argent),
            Choice("4) Upgrade argent account", upgrade_argent),
            Choice("5) Bridge on Orbiter", bridge_orbiter),
            Choice("6) Make swap on JediSwap", swap_jediswap),
            Choice("7) Make swap on MySwap", swap_myswap),
            Choice("8) Make swap on 10kSwap", swap_starkswap),
            Choice("9) Make swap on SithSwap", swap_sithswap),
            Choice("10) Make swap on Avnu", swap_avnu),
            Choice("11) Make swap on Protoss", swap_protoss),
            Choice("12) Deposit ZkLend", deposit_zklend),
            Choice("13) Deposit Nostra", deposit_nostra),
            Choice("14) Withdraw ZkLend", withdraw_zklend),
            Choice("15) Withdraw Nostra", withdraw_nostra),
            Choice("16) Enable collateral ZkLend", enable_collateral_zklend),
            Choice("17) Disable collateral ZkLend", disable_collateral_zklend),
            Choice("18) Mint Starknet ID", mint_starknet_id),
            Choice("19) Dmail send mail", send_mail_dmail),
            Choice("20) Mint StarkStars NFT", mint_starkstars),
            Choice("21) Mint NFT on Pyramid", create_collection_pyramid),
            Choice("22) Unframed", cancel_order_unframed),
            Choice("23) Flex", cancel_order_flex),
            Choice("24) Mint Gol token", mint_gol),
            Choice("25) Deploy token", deploy_token),
            Choice("26) Deploy and mint NFT", deploy_nft),
            Choice("27) Transfer", make_transfer),
            Choice("28) Swap tokens to ETH", swap_tokens),
            Choice("29) Use Multiswap", swap_multiswap),
            Choice("30) Use custom routes ", custom_routes),
            Choice("31) Check transaction count", "tx_checker"),
            Choice("32) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        print("\n❤️ Subscribe to me – https://t.me/sybilwave\n")
        print("🤑 Donate me: 0x00000b0ddce0bfda4531542ad1f2f5fad7b9cde9")
        sys.exit()
    return result


def get_wallets(use_recipients: bool = False):
    if use_recipients:
        account_with_recipients = dict(zip(ACCOUNTS, RECIPIENTS))

        wallets = [
            {
                "id": _id,
                "key": key,
                "recipient": account_with_recipients[key],
            } for _id, key in enumerate(account_with_recipients, start=1)
        ]
    else:
        wallets = [
            {
                "id": _id,
                "key": key,
            } for _id, key in enumerate(ACCOUNTS, start=1)
        ]

    return wallets


async def run_module(module, account_id, key, recipient: Union[str, None] = None):
    try:
        if recipient:
            await module(account_id, key, TYPE_WALLET, recipient)
        else:
            await module(account_id, key, TYPE_WALLET)
    except Exception as e:
        logger.error(e)

    if REMOVE_WALLET:
        remove_wallet(key, recipient)

    await sleep(SLEEP_FROM, SLEEP_TO)


def _async_run_module(module, account_id, key, recipient):
    asyncio.run(run_module(module, account_id, key, recipient))


def main(module):
    if module in [deposit_starknet, withdraw_starknet, bridge_orbiter, make_transfer]:
        wallets = get_wallets(True)
    else:
        wallets = get_wallets()

    if RANDOM_WALLET:
        random.shuffle(wallets)

    with ThreadPoolExecutor(max_workers=QUANTITY_THREADS) as executor:
        for _, account in enumerate(wallets, start=1):
            executor.submit(
                _async_run_module,
                module,
                account.get("id"),
                account.get("key"),
                account.get("recipient", None)
            )
            time.sleep(random.randint(THREAD_SLEEP_FROM, THREAD_SLEEP_TO))


if __name__ == '__main__':
    print("❤️ Subscribe to me – https://t.me/sybilwave\n")

    logger.add("logging.log")

    module = get_module()
    if module == "tx_checker":
        get_tx_count(TYPE_WALLET)
    else:
        main(module)

    print("\n❤️ Subscribe to me – https://t.me/sybilwave\n")
    print("🤑 Donate me: 0x00000b0ddce0bfda4531542ad1f2f5fad7b9cde9")
