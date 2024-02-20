import time

import requests
import random
import sys
from typing import Union, List

from loguru import logger
from starknet_py.cairo.felt import decode_shortstring
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId, Invoke
from starknet_py.net.signer.stark_curve_signer import KeyPair
from web3 import Web3

from settings import CAIRO_VERSION, FEE_MULTIPLIER

from config import (
    BRAAVOS_PROXY_CLASS_HASH,
    BRAAVOS_IMPLEMENTATION_CLASS_HASH,
    ARGENTX_PROXY_CLASS_HASH,
    ARGENTX_IMPLEMENTATION_CLASS_HASH,
    ERC20_ABI,
    STARKNET_TOKENS,
    SPACESHARD_API,
    WITHDRAW_ABI,
    RPC,
    ARGENTX_IMPLEMENTATION_CLASS_HASH_NEW,
    ARGENTX_IMPLEMENTATION_CLASS_HASH_STRK,
    BRIDGE_CONTRACTS,
    ARGENT_ABI, BRAAVOS_IMPLEMENTATION_CLASS_HASH_NEW, BRAAVOS_ABI, BRAAVOS_REGENESIS_ACCOUNT_ID
)
from utils.gas_checker import check_gas
from utils.helpers import retry


class Starknet:

    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        self._id = _id
        self.key_pair = KeyPair.from_private_key(private_key)
        self.client = FullNodeClient(random.choice(RPC["starknet"]["rpc"]))
        self.address = self._create_account(type_account)
        self.account = Account(
            address=self.address,
            client=self.client,
            key_pair=self.key_pair,
            chain=StarknetChainId.MAINNET,
        )
        self.account.ESTIMATED_FEE_MULTIPLIER = FEE_MULTIPLIER
        self.explorer = RPC["starknet"]["explorer"]

    def _create_account(self, type_account) -> Union[int, None]:
        if type_account == "argent":
            return self._get_argent_address()
        elif type_account == "braavos":
            return self._get_braavos_account()
        else:
            logger.error("Type wallet error! Available values: argent or braavos")
            sys.exit()

    def _get_argent_address(self) -> int:
        if CAIRO_VERSION == 0:
            selector = get_selector_from_name("initialize")

            calldata = [self.key_pair.public_key, 0]

            address = compute_address(
                class_hash=ARGENTX_PROXY_CLASS_HASH,
                constructor_calldata=[ARGENTX_IMPLEMENTATION_CLASS_HASH, selector, len(calldata), *calldata],
                salt=self.key_pair.public_key,
            )
        else:
            address = compute_address(
                class_hash=ARGENTX_IMPLEMENTATION_CLASS_HASH_NEW,
                constructor_calldata=[self.key_pair.public_key, 0],
                salt=self.key_pair.public_key,
            )

        return address

    def _get_braavos_account(self) -> int:
        selector = get_selector_from_name("initializer")

        calldata = [self.key_pair.public_key]

        address = compute_address(
            class_hash=BRAAVOS_PROXY_CLASS_HASH,
            constructor_calldata=[BRAAVOS_IMPLEMENTATION_CLASS_HASH, selector, len(calldata), *calldata],
            salt=self.key_pair.public_key,
        )

        return address

    def get_contract(self, contract_address: int, abi: Union[dict, None] = None, cairo_version: int = 0):
        if abi is None:
            abi = ERC20_ABI

        contract = Contract(address=contract_address, abi=abi, provider=self.account, cairo_version=cairo_version)

        return contract

    async def get_balance(self, contract_address: int) -> dict:
        contract = self.get_contract(contract_address)

        symbol_data = await contract.functions["symbol"].call()
        symbol = decode_shortstring(symbol_data.symbol)

        decimal = await contract.functions["decimals"].call()

        balance_wei = await contract.functions["balanceOf"].call(self.address)

        balance = balance_wei.balance / 10 ** decimal.decimals

        return {"balance_wei": balance_wei.balance, "balance": balance, "symbol": symbol, "decimal": decimal.decimals}

    async def get_amount(
            self,
            from_token: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        random_amount = round(random.uniform(min_amount, max_amount), decimal)
        random_percent = random.randint(min_percent, max_percent)
        percent = 1 if random_percent == 100 else random_percent / 100

        if from_token == "ETH":
            balance = await self.account.get_balance()
            amount_wei = int(balance * percent) if all_amount else Web3.to_wei(random_amount, "ether")
            amount = Web3.from_wei(int(balance * percent), "ether") if all_amount else random_amount
        else:
            balance = await self.get_balance(STARKNET_TOKENS[from_token])
            amount_wei = int(balance["balance_wei"] * percent) \
                if all_amount else int(random_amount * 10 ** balance["decimal"])
            amount = balance["balance"] * percent if all_amount else random_amount
            balance = balance["balance_wei"]

        return amount_wei, amount, balance

    async def sign_transaction(self, calls: List[Call]):
        transaction = await self.account.sign_invoke_transaction(
            calls=calls,
            auto_estimate=True,
            nonce=await self.account.get_nonce(),
        )

        return transaction

    async def send_transaction(self, transaction: Invoke):
        transaction_response = await self.account.client.send_transaction(transaction)

        return transaction_response

    async def wait_until_tx_finished(self, tx_hash: int):
        await self.account.client.wait_for_tx(tx_hash, check_interval=10)

        logger.success(f"[{self._id}][{hex(self.address)}] {self.explorer}{hex(tx_hash)} successfully!")

    async def get_transaction(self, tx_hash: int):
        transaction_data = await self.account.client.get_transaction_receipt(tx_hash)

        return transaction_data

    @retry
    @check_gas("starknet")
    async def withdraw(
            self,
            recipient: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        amount_wei, amount, balance = await self.get_amount(
            "ETH",
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{hex(self.address)}] Withdraw from Starknet | {amount} ETH")

        spaceshard_contract = self.get_contract(STARKNET_TOKENS["ETH"])
        bridge_contract = self.get_contract(BRIDGE_CONTRACTS["withdraw"], WITHDRAW_ABI)

        gas_cost = requests.get(
            SPACESHARD_API +
            f"{BRIDGE_CONTRACTS['withdraw']}/" +
            str(int(time.time()))
        )

        transfer_to_spaceshard = spaceshard_contract.functions["transfer"].prepare(
            0x06e02b62e101b44382d030d7aee5528bf65eed13d3b2d5da3dfa883a2e1ce5f7,
            int(gas_cost.json()["result"]["gasCost"])
        )

        initiate_withdraw = bridge_contract.functions["initiate_withdraw"].prepare(
            int(recipient, 16),
            amount_wei
        )

        transaction = await self.sign_transaction([transfer_to_spaceshard, initiate_withdraw])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)

    @retry
    @check_gas("starknet")
    async def deploy_argent(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Deploy argent account")

        class_hash = ARGENTX_IMPLEMENTATION_CLASS_HASH_NEW

        transaction = await self.account.deploy_account(
            address=self.address,
            class_hash=class_hash,
            salt=self.key_pair.public_key,
            key_pair=self.key_pair,
            client=self.client,
            chain=StarknetChainId.MAINNET,
            constructor_calldata=[self.key_pair.public_key, 0],
            auto_estimate=True
        )

        await self.wait_until_tx_finished(transaction.hash)

    @retry
    @check_gas("starknet")
    async def upgrade_argent(self):
        class_hash = ARGENTX_IMPLEMENTATION_CLASS_HASH_NEW

        contract = self.get_contract(self.address, ARGENT_ABI)

        account_version = await contract.functions["getVersion"].call()

        version = bytes.fromhex(hex(account_version.as_tuple()[0])[2:]).decode("utf8")

        if version == "0.2.3":
            logger.info(f"[{self._id}][{hex(self.address)}] Upgrade account to cairo 1")

            upgrade_call = contract.functions["upgrade"].prepare(class_hash, [0])

            transaction = await self.sign_transaction([upgrade_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.info(f"[{self._id}][{hex(self.address)}] No upgrade required")

    @retry
    @check_gas("starknet")
    async def argentx_enable_strk(self):
        class_hash = ARGENTX_IMPLEMENTATION_CLASS_HASH_STRK

        contract = self.get_contract(self.address, ARGENT_ABI)

        account_version = await contract.functions["getVersion"].call()

        version = bytes.fromhex(hex(account_version.as_tuple()[0])[2:]).decode("utf8")

        if version == "0.3.0":
            logger.info(f"[{self._id}][{hex(self.address)}] Upgrade account to v0.3.1 (enabling STRK fee)")

            upgrade_call = contract.functions["upgrade"].prepare(class_hash, [0])

            transaction = await self.sign_transaction([upgrade_call])

            transaction_response = await self.send_transaction(transaction)

            await self.wait_until_tx_finished(transaction_response.transaction_hash)
        else:
            logger.info(f"[{self._id}][{hex(self.address)}] No upgrade required")

    @retry
    @check_gas("starknet")
    async def upgrade_braavos(self):
        contract = self.get_contract(self.address, BRAAVOS_ABI)

        logger.info(f"[{self._id}][{hex(self.address)}] Upgrade account to cairo 1")

        upgrade_call = contract.functions["upgrade_regenesis"].prepare(
            BRAAVOS_IMPLEMENTATION_CLASS_HASH_NEW,
            BRAAVOS_REGENESIS_ACCOUNT_ID
        )

        transaction = await self.sign_transaction([upgrade_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
