"""76 Verified GitHub Repositories

All repos verified to exist via GitHub API.
Last verified: 2026-03-26
"""

TRUSTED_BSC_REPOS = [
    # BSC Ecosystem
    {
        "name": "pancakeswap/pancake-frontend",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "pancakeswap/pancake-toolkit",
        "type": "SDK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "pancakeswap/pancake-swap-sdk",
        "type": "SDK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "VenusProtocol/venus-protocol",
        "type": "Lending",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "VenusProtocol/vips",
        "type": "Governance",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "alpaca-finance/bsc-alpaca-contract",
        "type": "Yield",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "bnb-chain/bsc",
        "type": "Chain",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "bnb-chain/bnb-chain-tutorial",
        "type": "Docs",
        "priority": 2,
        "has_bounties": False,
        "pays": False,
        "reputation": "high",
    },
    {
        "name": "bnb-chain/bsc-genesis-contract",
        "type": "Contract",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "bnb-chain/greenfield",
        "type": "Storage",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "bnb-chain/opbnb",
        "type": "L2",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "pancakeswap/pancake-v3-contracts",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "FraxFinance/frax-solidity",
        "type": "Protocol",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "Curvefi/curve-contract",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "Synthetixio/synthetix",
        "type": "Derivatives",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    # DeFi Protocols
    {
        "name": "compound-finance/compound-protocol",
        "type": "Lending",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "aave/aave-v3-core",
        "type": "Lending",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "uniswap/uniswap-v3-core",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "sushiswap/sushiswap",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "balancer/balancer-v2-monorepo",
        "type": "DEX",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "yearn/yearn-vaults-v3",
        "type": "Yield",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "makerdao/dss",
        "type": "Stablecoin",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "Layr-Labs/eigenlayer-contracts",
        "type": "Restaking",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    # Security & Tools
    {
        "name": "OpenZeppelin/openzeppelin-contracts",
        "type": "Security",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "Consensys/solidity-antlr4",
        "type": "Parser",
        "priority": 2,
        "has_bounties": False,
        "pays": False,
        "reputation": "high",
    },
    {
        "name": "crytic/slither",
        "type": "Security",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "trailofbits/not-so-smart-contracts",
        "type": "Security",
        "priority": 2,
        "has_bounties": False,
        "pays": False,
        "reputation": "high",
    },
    {
        "name": "transmissions11/solmate",
        "type": "Library",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Dev Tools
    {
        "name": "scaffold-eth/scaffold-eth-2",
        "type": "DevTool",
        "priority": 2,
        "has_bounties": False,
        "pays": False,
        "reputation": "high",
    },
    {
        "name": "foundry-rs/foundry",
        "type": "DevTool",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    # Ethereum Core
    {
        "name": "ethereum/solidity",
        "type": "Language",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "ethereum/go-ethereum",
        "type": "Client",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "ethereum/web3.py",
        "type": "Library",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "ethers-io/ethers.js",
        "type": "Library",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "web3/web3.js",
        "type": "Library",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "OpenZeppelin/openzeppelin-upgrades",
        "type": "Library",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "wagmi-dev/wagmi",
        "type": "React",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "OpenZeppelin/openzeppelin-contracts-upgradeable",
        "type": "NFT",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Bridges
    {
        "name": "LayerZero-Labs/layerzero-v1",
        "type": "Bridge",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "wormhole-foundation/wormhole",
        "type": "Bridge",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "celo-org/celo-monorepo",
        "type": "Chain",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Wallets
    {
        "name": "MetaMask/metamask-extension",
        "type": "Wallet",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "rainbow-me/rainbow",
        "type": "Wallet",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "trustwallet/wallet-core",
        "type": "Wallet",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "safe-global/safe-contracts",
        "type": "Wallet",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "ledgerHQ/ledger-live",
        "type": "Wallet",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Oracles
    {
        "name": "smartcontractkit/chainlink",
        "type": "Oracle",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "BandProtocol/bandchain",
        "type": "Oracle",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Staking
    {
        "name": "ethereum/staking-deposit-cli",
        "type": "Staking",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "rocket-pool/rocketpool",
        "type": "Staking",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "stakewise/v3-core",
        "type": "Staking",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Governance
    {
        "name": "snapshot-labs/snapshot",
        "type": "Governance",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "compound-finance/compound-governance",
        "type": "Governance",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "openzeppelin/defender-client",
        "type": "Governance",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Analytics
    {
        "name": "blockscout/blockscout",
        "type": "Explorer",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "DefiLlama/DefiLlama-Adapters",
        "type": "Analytics",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # ZK
    {
        "name": "matter-labs/zksync-era",
        "type": "ZK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "starkware-libs/starkex-contracts",
        "type": "ZK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "0xPolygonHermez/zkevm-contracts",
        "type": "ZK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "scroll-tech/scroll-contracts",
        "type": "ZK",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Other Chains
    {
        "name": "cosmos/cosmos-sdk",
        "type": "Chain",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "polkadot-js/api",
        "type": "Chain",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "near/nearcore",
        "type": "Chain",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "solana-labs/solana",
        "type": "Chain",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "highest",
    },
    {
        "name": "cardano-foundation/cardano-wallet",
        "type": "Chain",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Testing & Tools
    {
        "name": "sc-forks/solidity-coverage",
        "type": "Testing",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "protofire/solhint",
        "type": "Linter",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "consensys/surya",
        "type": "Analysis",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "eth-brownie/brownie",
        "type": "Framework",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "trufflesuite/truffle",
        "type": "Framework",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Documentation
    {
        "name": "ethereumbook/ethereumbook",
        "type": "Docs",
        "priority": 3,
        "has_bounties": False,
        "pays": False,
        "reputation": "medium",
    },
    {
        "name": "Consensys/ethereum-developer-tools-list",
        "type": "Docs",
        "priority": 3,
        "has_bounties": False,
        "pays": False,
        "reputation": "medium",
    },
    {
        "name": "ethereum/EIPs",
        "type": "Standards",
        "priority": 2,
        "has_bounties": False,
        "pays": False,
        "reputation": "highest",
    },
    {
        "name": "ethereum/solc-bin",
        "type": "Compiler",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    {
        "name": "ethereum/solc-js",
        "type": "Compiler",
        "priority": 2,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
    # Uniswap v4
    {
        "name": "uniswapfoundation/v4-template",
        "type": "SDK",
        "priority": 1,
        "has_bounties": True,
        "pays": True,
        "reputation": "high",
    },
]


def get_trusted_repos(limit: int = None) -> list:
    """Get trusted repos, optionally limited."""
    if limit:
        return TRUSTED_BSC_REPOS[:limit]
    return TRUSTED_BSC_REPOS


def get_repos_by_priority(priority: int) -> list:
    """Get repos filtered by priority."""
    return [r for r in TRUSTED_BSC_REPOS if r["priority"] == priority]


def get_bounty_repos() -> list:
    """Get repos that have bounties."""
    return [r for r in TRUSTED_BSC_REPOS if r.get("has_bounties")]


def get_paying_repos() -> list:
    """Get repos that pay."""
    return [r for r in TRUSTED_BSC_REPOS if r.get("pays")]


if __name__ == "__main__":
    repos = get_trusted_repos()
    print(f"Total trusted repos: {len(repos)}")
    print(f"Priority 1: {len(get_repos_by_priority(1))}")
    print(f"Priority 2: {len(get_repos_by_priority(2))}")
    print(f"Priority 3: {len(get_repos_by_priority(3))}")
    print(f"Has bounties: {len(get_bounty_repos())}")
    print(f"Pays: {len(get_paying_repos())}")
