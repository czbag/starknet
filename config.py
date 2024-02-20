import json

with open('data/rpc.json') as file:
    RPC = json.load(file)

with open("accounts.txt", "r") as file:
    ACCOUNTS = [row.strip() for row in file]

with open("recipients.txt", "r") as file:
    RECIPIENTS = [row.strip() for row in file]

with open('data/abi/erc20_abi.json') as file:
    ERC20_ABI = json.load(file)

with open('data/abi/abi.json') as file:
    ARGENT_ABI = json.load(file)

with open('data/abi/braavos/abi.json') as file:
    BRAAVOS_ABI = json.load(file)

with open('data/abi/bridge/deposit_abi.json') as file:
    DEPOSIT_ABI = json.load(file)

with open('data/abi/bridge/withdraw_abi.json') as file:
    WITHDRAW_ABI = json.load(file)

with open('data/abi/orbiter/deposit.json') as file:
    ORBITER_DEPOSIT_ABI = json.load(file)

with open('data/abi/orbiter/withdraw.json') as file:
    ORBITER_WITHDRAW_ABI = json.load(file)

with open('data/abi/jediswap/abi.json') as file:
    JEDISWAP_ABI = json.load(file)

with open('data/abi/myswap/abi.json') as file:
    MYSWAP_ABI = json.load(file)

with open('data/abi/10kswap/abi.json') as file:
    STARKSWAP_ABI = json.load(file)

with open('data/abi/sithswap/abi.json') as file:
    SITHSWAP_ABI = json.load(file)

with open('data/abi/protoss/abi.json') as file:
    PROTOSS_ABI = json.load(file)

with open('data/abi/zklend/abi.json') as file:
    ZKLEND_ABI = json.load(file)

with open('data/abi/nostra/abi.json') as file:
    NOSTRA_ABI = json.load(file)

with open('data/abi/dmail/abi.json') as file:
    DMAIL_ABI = json.load(file)

with open('data/abi/starknet_id/abi.json') as file:
    STARKNET_ID_ABI = json.load(file)

with open('data/abi/pyramid/abi.json') as file:
    PYRAMID_ABI = json.load(file)

with open('data/abi/unframed/abi.json') as file:
    UNFRAMED_ABI = json.load(file)

with open('data/abi/flex/abi.json') as file:
    FLEX_ABI = json.load(file)

with open('data/abi/starkstars/abi.json') as file:
    STARKSTARS_ABI = json.load(file)

with open('data/abi/starkguardians/abi.json') as file:
    STARKGUARDIANS_ABI = json.load(file)

with open('data/abi/gol2/abi.json') as file:
    GOL2_ABI = json.load(file)

with open('data/abi/starkverse/abi.json') as file:
    STARKVERSE_ABI = json.load(file)

with open('data/abi/almanac/abi.json') as file:
    ALMANAC_ABI = json.load(file)

with open('data/abi/ninth/abi.json') as file:
    NINTH_ABI = json.load(file)

SPACESHARD_API = "https://starkgate.spaceshard.io/v1/gas-cost/"

BRAAVOS_PROXY_CLASS_HASH = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
BRAAVOS_IMPLEMENTATION_CLASS_HASH = 0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570
BRAAVOS_IMPLEMENTATION_CLASS_HASH_NEW = 0x816dd0297efc55dc1e7559020a3a825e81ef734b558f03c83325d4da7e6253
BRAAVOS_REGENESIS_ACCOUNT_ID = 0x2ceccef7f994940b3962a6c67e0ba4fcd37df7d131417c604f91e03caecc1cd

ARGENTX_PROXY_CLASS_HASH = 0x025EC026985A3BF9D0CC1FE17326B245DFDC3FF89B8FDE106542A3EA56C5A918
ARGENTX_IMPLEMENTATION_CLASS_HASH = 0x33434AD846CDD5F23EB73FF09FE6FDDD568284A0FB7D1BE20EE482F044DABE2
ARGENTX_IMPLEMENTATION_CLASS_HASH_NEW = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003
ARGENTX_IMPLEMENTATION_CLASS_HASH_STRK = 0x29927c8af6bccf3f6fda035981e765a7bdbf18a2dc0d630494f8758aa908e2b

BRIDGE_CONTRACTS = {
    "deposit": "0xae0ee0a63a2ce6baeeffe56e7714fb4efe48d419",
    "withdraw": "0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
}

ORBITER_CONTRACTS = {
    "bridge": "0xd9d74a29307cc6fc8bf424ee4217f1a587fbc8dc",
    "deposit": "",
    "withdraw": 0x173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b
}

STARKNET_TOKENS = {
    "ETH": 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
    "USDC": 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8,
    "DAI": 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3,
    "USDT": 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8,
    "STRK": 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
}

JEDISWAP_CONTRACT = 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023

MYSWAP_CONTRACT = 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28

STARKSWAP_CONTRACT = 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1

SITHSWAP_CONTRACT = 0x28c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627

PROTOSS_CONTRACT = 0x07a0922657e550ba1ef76531454cb6d203d4d168153a0f05671492982c2f7741

AVNU_CONTRACT = {
    "router": 0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f,
    "use_ref": True  # If you use True, you support me 1% of the transaction amount
}

ZKLEND_CONCTRACTS = {
    "router": 0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05,
    "ETH": 0x01b5bd713e72fdc5d63ffd83762f81297f6175a5e0a4771cdadbc1dd5fe72cb1,
    "USDC": 0x047ad51726d891f972e74e4ad858a261b43869f7126ce7436ee0b2529a98f486,
    "DAI": 0x062fa7afe1ca2992f8d8015385a279f49fad36299754fb1e9866f4f052289376,
    "USDT": 0x00811d8da5dc8a2206ea7fd0b28627c2d77280a515126e62baa4d78e22714c4a
}

NOSTRA_CONTRACTS = {
    "ETH": 0x07170f54dd61ae85377f75131359e3f4a12677589bb7ec5d61f362915a5c0982,
    "USDC": 0x06eda767a143da12f70947192cd13ee0ccc077829002412570a88cd6539c1d85,
    "DAI": 0x04f18ffc850cdfa223a530d7246d3c6fc12a5969e0aa5d4a88f470f5fe6c46e9,
    "USDT": 0x0453c4c996f1047d9370f824d68145bd5e7ce12d00437140ad02181e1d11dc83,
}

DMAIL_CONTRACT = 0x0454f0bd015e730e5adbb4f080b075fdbf55654ff41ee336203aa2e1ac4d4309

STARKNET_ID_CONTRACT = 0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af

PYRAMID_CONTRACT = 0x042e7815d9e90b7ea53f4550f74dc12207ed6a0faaef57ba0dbf9a66f3762d82

UNFRAMED_CONTRACT = 0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b

FLEX_CONTRACT = 0x04b1b3fdf34d00288a7956e6342fb366a1510a9387d321c87f3301d990ac19d4

STARKGUARDIANS_CONTRACT = 0x041a78e741e5af2fec34b695679bc6891742439f7afb8484ecd7766661ad02bf

GOL2_CONTRACT = 0x06a05844a03bb9e744479e3298f54705a35966ab04140d3d8dd797c1f6dc49d0

STARKVERSE_CONTRACT = 0x060582df2cd4ad2c988b11fdede5c43f56a432e895df255ccd1af129160044b8

ALMANAC_CONTRACT = 0x07d4dc2bf13ede97b9e458dc401d4ff6dd386a02049de879ebe637af8299f91d

NINTH_CONTRACT = 0x07038b75cd6557f4c788971eacc37cf6554acad7146398d42bcc7da3a05b5218
