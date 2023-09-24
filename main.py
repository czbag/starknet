import asyncio
import random
import sys
from typing import Union

import questionary
from questionary import Choice

from config import ACCOUNTS, RECIPIENTS
from utils.sleeping import sleep
from modules_settings import *
from settings import TYPE_WALLET, RANDOM_WALLET, IS_SLEEP, SLEEP_FROM, SLEEP_TO


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
            Choice("10) Make swap on Fibrous", swap_fibrous),
            Choice("11) Deposit ZkLend", deposit_zklend),
            Choice("12) Withdraw ZkLend", withdraw_zklend),
            Choice("13) Enable collateral ZkLend", enable_collateral_zklend),
            Choice("14) Disable collateral ZkLend", disable_collateral_zklend),
            Choice("15) Mint Starknet ID", mint_starknet_id),
            Choice("16) Dmail send mail", send_mail_dmail),
            Choice("17) Mint StarkVerse NFT", mint_starkverse),
            Choice("18) Transfer", make_transfer),
            Choice("19) Use Multiswap", swap_multiswap),
            Choice("20) Use custom routes ", custom_routes),
            Choice("21) Check transaction count", "tx_checker"),
            Choice("22) Exit", "exit"),
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


def run_module(module, account_id, key, recipient: Union[str, None] = None):
    if recipient:
        asyncio.run(module(account_id, key, TYPE_WALLET, recipient))
    else:
        asyncio.run(module(account_id, key, TYPE_WALLET))


def main(module):
    if module in [deposit_starknet, withdraw_starknet, bridge_orbiter, make_transfer]:
        wallets = get_wallets(True)
    else:
        wallets = get_wallets()

    if RANDOM_WALLET:
        random.shuffle(wallets)

    for account in wallets:
        run_module(module, account.get("id"), account.get("key"), account.get("recipient", None))

        if account != wallets[-1] and IS_SLEEP:
            sleep(SLEEP_FROM, SLEEP_TO)


if __name__ == '__main__':
    print("❤️ Subscribe to me – https://t.me/sybilwave\n")

    module = get_module()
    if module == "tx_checker":
        get_tx_count(TYPE_WALLET)
    else:
        main(module)

    print("\n❤️ Subscribe to me – https://t.me/sybilwave\n")
    print("🤑 Donate me: 0x00000b0ddce0bfda4531542ad1f2f5fad7b9cde9")
