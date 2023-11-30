import aiohttp
from loguru import logger
from web3 import Web3

from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Account, Starknet
from config import ORBITER_CONTRACTS, ORBITER_DEPOSIT_ABI, STARKNET_TOKENS, ORBITER_WITHDRAW_ABI


class Orbiter:
    def __init__(self, _id: int, private_key: str, type_account: str, recipient: str) -> None:
        self._id = _id
        self.private_key = private_key
        self.recipient = recipient
        self.type_account = type_account

        self.chain_ids = {
            "ethereum": "1",
            "arbitrum": "42161",
            "optimism": "10",
            "zksync": "324",
            "nova": "42170",
            "zkevm": "1101",
            "scroll": "534352",
            "base": "8453",
            "linea": "59144",
            "zora": "7777777",
            "starknet": "SN_MAIN",
        }

    @retry
    async def get_bridge_amount(self, from_chain: str, to_chain: str, address: str, amount: float):
        url = "https://openapi.orbiter.finance/explore/v3/yj6toqvwh1177e1sexfy0u1pxx5j8o47"

        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "orbiter_calculatedAmount",
            "params": [f"{self.chain_ids[from_chain]}-{self.chain_ids[to_chain]}:ETH-ETH", float(amount)]
        }

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=url,
                headers={"Content-Type": "application/json"},
                json=data,
            )

            response_data = await response.json()

            if response_data.get("result").get("error", None) is None:
                return int(response_data.get("result").get("_sendValue"))

            else:
                error_data = response_data.get("result").get("error")

                logger.error(f"[{self._id}][{address}] Orbiter error | {error_data}")

                return False

    @check_gas("ethereum")
    async def bridge_to_starknet(
            self,
            from_chain: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        eth_account = Account(self._id, self.private_key, self.recipient, chain=from_chain)

        amount_wei, amount, balance = await eth_account.get_amount(
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(f"[{self._id}][{eth_account.address}] Orbiter bridge to Starknet | {amount} ETH")

        if ORBITER_CONTRACTS["deposit"] == "":
            logger.error(f"[{self._id}][{eth_account.address}] Don't have orbiter contract")
            return

        bridge_amount = await self.get_bridge_amount(from_chain, "starknet", eth_account.address, amount)

        if bridge_amount is False:
            return

        if bridge_amount > balance:
            logger.error(f"[{self._id}][{eth_account.address}] Insufficient funds!")
        else:
            contract = eth_account.get_contract(ORBITER_CONTRACTS["bridge"], ORBITER_DEPOSIT_ABI)

            tx = {
                "chainId": await eth_account.w3.eth.chain_id,
                "from": eth_account.address,
                "value": bridge_amount,
                "nonce": await eth_account.w3.eth.get_transaction_count(eth_account.address)
            }

            recipient = "0x03" + self.recipient[2:]

            transaction = await contract.functions.transfer(
                Web3.to_checksum_address(ORBITER_CONTRACTS["deposit"]),
                recipient
            ).build_transaction(tx)

            signed_txn = await eth_account.sign(transaction)

            txn_hash = await eth_account.send_raw_transaction(signed_txn)

            await eth_account.wait_until_tx_finished(txn_hash)

    @check_gas("starknet")
    async def bridge_to_evm(
            self,
            to_chain: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):
        starknet_account = Starknet(self._id, self.private_key, self.type_account)

        amount_wei, amount, balance = await starknet_account.get_amount(
            "ETH",
            min_amount,
            max_amount,
            decimal,
            all_amount,
            min_percent,
            max_percent
        )

        logger.info(
            f"[{self._id}][{hex(starknet_account.address)}] Orbiter bridge to {to_chain.title()} | {amount} ETH"
        )

        bridge_amount = await self.get_bridge_amount("starknet", to_chain, hex(starknet_account.address), amount)

        bridge_contract = starknet_account.get_contract(ORBITER_CONTRACTS["withdraw"], ORBITER_WITHDRAW_ABI)
        approve_contract = starknet_account.get_contract(STARKNET_TOKENS["ETH"])

        approve_call = approve_contract.functions["approve"].prepare(ORBITER_CONTRACTS["withdraw"], 2 ** 128)

        transfer_call = bridge_contract.functions["transferERC20"].prepare(
            STARKNET_TOKENS["ETH"],
            0x64a24243f2aabae8d2148fa878276e6e6e452e3941b417f3c33b1649ea83e11,
            bridge_amount,
            int(self.recipient, 16)
        )

        transaction = await starknet_account.sign_transaction([approve_call, transfer_call])

        transaction_response = await starknet_account.send_transaction(transaction)

        await starknet_account.wait_until_tx_finished(transaction_response.transaction_hash)

    @retry
    async def bridge(
            self,
            from_chain: str,
            to_chain: str,
            min_amount: float,
            max_amount: float,
            decimal: int,
            all_amount: bool,
            min_percent: int,
            max_percent: int
    ):

        if from_chain != "starknet":
            await self.bridge_to_starknet(
                from_chain, min_amount, max_amount, decimal, all_amount, min_percent, max_percent
            )
        else:
            await self.bridge_to_evm(to_chain, min_amount, max_amount, decimal, all_amount, min_percent, max_percent)
