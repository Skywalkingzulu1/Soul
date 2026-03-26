"""Crypto Earning Strategies - Open Source Focused

Creative ways to earn crypto through open source:
1. Bounties - Gitcoin, Layer3, HackerOne
2. Airdrops - Protocol launches
3. Grants - Foundation grants
4. Yield - Liquidity provision
5. Staking - Validator rewards
6. Faucets - Testnet tokens
7. Governance - Voting rewards
8. Bug Bounties - Security audits
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class StrategyType(Enum):
    BOUNTY = "bounty"
    AIRDROP = "airdrop"
    GRANT = "grant"
    YIELD = "yield"
    STAKING = "staking"
    FAUCET = "faucet"
    GOVERNANCE = "governance"
    BUG_BOUNTY = "bug_bounty"
    LIQUIDITY = "liquidity"
    TRADING = "trading"


@dataclass
class CryptoStrategy:
    """A crypto earning strategy."""

    name: str
    type: StrategyType
    description: str
    risk_level: str  # low, medium, high
    potential_earnings: str
    time_commitment: str
    requirements: List[str]
    platforms: List[str]
    priority: int  # 1 = highest


# All crypto earning strategies
CRYPTO_STRATEGIES = [
    # Open Source Bounties (Highest Priority)
    CryptoStrategy(
        name="Gitcoin Bounties",
        type=StrategyType.BOUNTY,
        description="Complete bounties on Gitcoin for crypto rewards",
        risk_level="low",
        potential_earnings="$50-$5000 per bounty",
        time_commitment="2-8 hours",
        requirements=["GitHub account", "Solidity skills", "Web3 knowledge"],
        platforms=["gitcoin.co"],
        priority=1,
    ),
    CryptoStrategy(
        name="Layer3 Quests",
        type=StrategyType.BOUNTY,
        description="Complete quests and earn tokens",
        risk_level="low",
        potential_earnings="$10-$500 per quest",
        time_commitment="1-4 hours",
        requirements=["Web3 wallet", "Basic DeFi knowledge"],
        platforms=["layer3.xyz"],
        priority=1,
    ),
    CryptoStrategy(
        name="HackerOne Bounties",
        type=StrategyType.BUG_BOUNTY,
        description="Find security vulnerabilities in crypto projects",
        risk_level="low",
        potential_earnings="$100-$100000 per bug",
        time_commitment="4-20 hours",
        requirements=["Security skills", "Smart contract auditing"],
        platforms=["hackerone.com"],
        priority=1,
    ),
    CryptoStrategy(
        name="Code4rena Audits",
        type=StrategyType.BUG_BOUNTY,
        description="Participate in smart contract audits",
        risk_level="low",
        potential_earnings="$500-$50000 per audit",
        time_commitment="8-40 hours",
        requirements=["Solidity expertise", "Security knowledge"],
        platforms=["code4rena.com"],
        priority=1,
    ),
    # Airdrops (Medium Priority)
    CryptoStrategy(
        name="Protocol Airdrops",
        type=StrategyType.AIRDROP,
        description="Claim tokens from new protocol launches",
        risk_level="low",
        potential_earnings="$100-$10000 per airdrop",
        time_commitment="1-2 hours",
        requirements=["Web3 wallet", "Protocol interaction"],
        platforms=["Multiple protocols"],
        priority=2,
    ),
    CryptoStrategy(
        name="Testnet Airdrops",
        type=StrategyType.AIRDROP,
        description="Participate in testnets for potential rewards",
        risk_level="low",
        potential_earnings="$50-$5000 per project",
        time_commitment="2-8 hours",
        requirements=["Testnet wallet", "Time to test"],
        platforms=["Multiple testnets"],
        priority=2,
    ),
    # Grants
    CryptoStrategy(
        name="Ethereum Foundation Grants",
        type=StrategyType.GRANT,
        description="Apply for grants to build on Ethereum",
        risk_level="low",
        potential_earnings="$10000-$500000",
        time_commitment="40-200 hours",
        requirements=["Strong proposal", "Track record"],
        platforms=["ethereum.org"],
        priority=2,
    ),
    CryptoStrategy(
        name="Protocol Grants",
        type=StrategyType.GRANT,
        description="Apply for grants from specific protocols",
        risk_level="low",
        potential_earnings="$5000-$100000",
        time_commitment="20-100 hours",
        requirements=["Relevant skills", "Good proposal"],
        platforms=["Various protocols"],
        priority=2,
    ),
    # Yield Strategies (Lower Priority)
    CryptoStrategy(
        name="Liquidity Provision",
        type=StrategyType.LIQUIDITY,
        description="Provide liquidity on DEXes for trading fees",
        risk_level="medium",
        potential_earnings="5-50% APY",
        time_commitment="1-2 hours setup",
        requirements=["Capital", "Understanding of IL"],
        platforms=["Uniswap", "PancakeSwap", "SushiSwap"],
        priority=3,
    ),
    CryptoStrategy(
        name="Yield Farming",
        type=StrategyType.YIELD,
        description="Stake LP tokens for additional rewards",
        risk_level="medium",
        potential_earnings="10-200% APY",
        time_commitment="2-4 hours setup",
        requirements=["Capital", "DeFi knowledge"],
        platforms=["Various DeFi protocols"],
        priority=3,
    ),
    CryptoStrategy(
        name="Staking",
        type=StrategyType.STAKING,
        description="Stake tokens for network validation rewards",
        risk_level="low",
        potential_earnings="3-15% APY",
        time_commitment="1 hour setup",
        requirements=["Minimum stake amount"],
        platforms=["Ethereum", "Cosmos", "Polkadot"],
        priority=3,
    ),
    # Governance
    CryptoStrategy(
        name="Governance Voting",
        type=StrategyType.GOVERNANCE,
        description="Vote on protocol proposals for rewards",
        risk_level="low",
        potential_earnings="$10-$100 per vote",
        time_commitment="30 minutes",
        requirements=["Governance tokens"],
        platforms=["Snapshot", "Tally"],
        priority=3,
    ),
    # Faucets
    CryptoStrategy(
        name="Testnet Faucets",
        type=StrategyType.FAUCET,
        description="Claim free testnet tokens",
        risk_level="low",
        potential_earnings="Free tokens (no direct value)",
        time_commitment="5 minutes",
        requirements=["Testnet wallet"],
        platforms=["Various faucets"],
        priority=4,
    ),
]


def get_strategies_by_type(strategy_type: StrategyType) -> List[CryptoStrategy]:
    """Get strategies filtered by type."""
    return [s for s in CRYPTO_STRATEGIES if s.type == strategy_type]


def get_strategies_by_priority(priority: int) -> List[CryptoStrategy]:
    """Get strategies filtered by priority."""
    return [s for s in CRYPTO_STRATEGIES if s.priority == priority]


def get_high_priority_strategies() -> List[CryptoStrategy]:
    """Get high priority strategies (priority 1)."""
    return get_strategies_by_priority(1)


def get_all_strategies() -> List[CryptoStrategy]:
    """Get all strategies."""
    return CRYPTO_STRATEGIES


def generate_crypto_tasks(
    strategies: List[CryptoStrategy], count: int = 6
) -> List[dict]:
    """Generate task data for crypto strategies."""
    tasks = []

    for strategy in strategies[:count]:
        task_data = {
            "strategy": strategy.name,
            "type": strategy.type.value,
            "platforms": strategy.platforms,
            "potential_earnings": strategy.potential_earnings,
            "risk_level": strategy.risk_level,
        }
        tasks.append(task_data)

    return tasks


if __name__ == "__main__":
    print("=== CRYPTO EARNING STRATEGIES ===\n")

    for priority in [1, 2, 3, 4]:
        strategies = get_strategies_by_priority(priority)
        if strategies:
            print(f"Priority {priority}:")
            for s in strategies:
                print(f"  - {s.name} ({s.type.value})")
                print(f"    Risk: {s.risk_level} | Earnings: {s.potential_earnings}")
                print(f"    Platforms: {', '.join(s.platforms)}")
            print()
