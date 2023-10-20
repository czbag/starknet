import asyncio
import random
import sys
from typing import Union

import questionary
from loguru import logger
from questionary import Choice

from config import ACCOUNTS, RECIPIENTS
from utils.helpers import get_run_accounts, update_run_accounts
from modules_settings import *
from settings import TYPE_WALLET, RANDOM_WALLET, SLEEP_FROM, SLEEP_TO, QUANTITY_RUN_ACCOUNTS


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Make deposit to Starknet", deposit_starknet),
            Choice("2) Make withdraw from Starknet", withdraw_starknet),
            Choice("3) Bridge on Orbiter", bridge_orbiter),
            Choice("4) Make swap on JediSwap", swap_jediswap),
            Choice("5) Make swap on MySwap", swap_myswap),
            Choice("6) Make swap on 10kSwap", swap_starkswap),
            Choice("7) Make swap on SithSwap", swap_sithswap),
            Choice("8) Make swap on Avnu", swap_avnu),
            Choice("9) Make swap on Protoss", swap_protoss),
            Choice("10) Deposit ZkLend", deposit_zklend),
            Choice("11) Withdraw ZkLend", withdraw_zklend),
            Choice("12) Enable collateral ZkLend", enable_collateral_zklend),
            Choice("13) Disable collateral ZkLend", disable_collateral_zklend),
            Choice("14) Mint Starknet ID", mint_starknet_id),
            Choice("15) Dmail send mail", send_mail_dmail),
            Choice("16) Mint StarkStars NFT", mint_starkstars),
            Choice("17) Mint StarkVerse NFT", mint_starkverse),
            Choice("18) Mint NFT on Pyramid", create_collection_pyramid),
            Choice("19) Unframed", cancel_order_unframed),
            Choice("20) Flex", cancel_order_flex),
            Choice("21) Transfer", make_transfer),
            Choice("22) Swap tokens to ETH", swap_tokens),
            Choice("23) Use Multiswap", swap_multiswap),
            Choice("24) Use custom routes ", custom_routes),
            Choice("25) Check transaction count", "tx_checker"),
            Choice("26) Exit", "exit"),
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


async def run_module(module, account_id, key, sleep_time, start_id, recipient: Union[str, None] = None):
    if start_id != 1:
        await asyncio.sleep(sleep_time)

    while True:
        run_accounts = get_run_accounts()

        if len(run_accounts["accounts"]) < QUANTITY_RUN_ACCOUNTS:
            update_run_accounts(account_id, "add")

            if recipient:
                await module(account_id, key, TYPE_WALLET, recipient)
            else:
                await module(account_id, key, TYPE_WALLET)

            update_run_accounts(account_id, "remove")

            break
        else:
            logger.info(f'Current run accounts: {len(run_accounts["accounts"])}')
            await asyncio.sleep(60)


async def main(module):
    if module in [deposit_starknet, withdraw_starknet, bridge_orbiter, make_transfer]:
        wallets = get_wallets(True)
    else:
        wallets = get_wallets()

    tasks = []

    sleep_time = random.randint(SLEEP_FROM, SLEEP_TO)

    if RANDOM_WALLET:
        random.shuffle(wallets)

    for _, account in enumerate(wallets, start=1):
        tasks.append(asyncio.create_task(
            run_module(module, account.get("id"), account.get("key"), sleep_time, _, account.get("recipient", None))
        ))

        sleep_time += random.randint(SLEEP_FROM, SLEEP_TO)

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    print("❤️ Subscribe to me – https://t.me/sybilwave\n")

    update_run_accounts(0, "new")

    module = get_module()
    if module == "tx_checker":
        get_tx_count(TYPE_WALLET)
    else:
        asyncio.run(main(module))

    print("\n❤️ Subscribe to me – https://t.me/sybilwave\n")
    print("🤑 Donate me: 0x00000b0ddce0bfda4531542ad1f2f5fad7b9cde9")
