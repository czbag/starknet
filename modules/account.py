import asyncio
import time
import random

from hexbytes import HexBytes
from loguru import logger
from web3 import Web3
from eth_account import Account as EthereumAccount
from web3.eth import AsyncEth
from web3.exceptions import TransactionNotFound

from config import RPC, ERC20_ABI
from settings import FEE_MULTIPLIER


class Account:
    def __init__(self, _id: int, private_key: str, recipient: str, chain: str = "ethereum") -> None:
        self._id = _id
        self.private_key = private_key
        self.recipient = recipient

        self.w3 = Web3(
            Web3.AsyncHTTPProvider(random.choice(RPC[chain]["rpc"])),
            modules={"eth": (AsyncEth,)},
        )
        self.account = EthereumAccount.from_key(private_key)
        self.address = self.account.address

        self.explorer = RPC[chain]["explorer"]

    def get_contract(self, contract_address: str, abi=None):
        contract_address = Web3.to_checksum_address(contract_address)

        if abi is None:
            abi = ERC20_ABI

        contract = self.w3.eth.contract(address=contract_address, abi=abi)

        return contract

    async def get_amount(
            self,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        random_amount = round(random.uniform(min_amount, max_amount), decimal)
        random_percent = random.randint(min_percent, max_percent)

        balance = await self.w3.eth.get_balance(self.address)
        amount_wei = int(balance / 100 * random_percent) if all_amount else Web3.to_wei(random_amount, "ether")
        amount = Web3.from_wei(int(balance / 100 * random_percent), "ether") if all_amount else random_amount

        return amount_wei, amount, balance

    async def wait_until_tx_finished(self, tx_hash: HexBytes, max_wait_time=180):
        start_time = time.time()
        while True:
            try:
                receipts = await self.w3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    logger.success(f"[{self._id}][{self.address}] {self.explorer}{tx_hash.hex()} successfully!")
                    return True
                elif status is None:
                    await asyncio.sleep(1)
                else:
                    logger.error(f"[{self._id}][{self.address}] {self.explorer}{tx_hash.hex()} transaction failed!")
                    return False
            except TransactionNotFound:
                if time.time() - start_time > max_wait_time:
                    print(f'FAILED TX: {tx_hash.hex()}')
                    return False
                await asyncio.sleep(1)

    async def sign(self, transaction):
        gas = await self.w3.eth.estimate_gas(transaction)
        gas = int(gas * FEE_MULTIPLIER)

        transaction.update({"gas": gas})

        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)

        return signed_txn

    async def send_raw_transaction(self, signed_txn):
        txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return txn_hash
