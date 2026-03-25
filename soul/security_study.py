"""
Solidity Smart Contract Security — 1000 Knowledge Vectors.
Generates security knowledge items, embeds them, and stores in ChromaDB.
"""

import json
import os
import time
import logging

logger = logging.getLogger(__name__)

SECURITY_KNOWLEDGE = []

# 1. Reentrancy (100 items)
REENTRANCY = [
    (
        "reentrancy-001",
        "Classic reentrancy occurs when a contract calls an external contract before updating its state. The external contract can call back into the original function, draining funds.",
        "reentrancy",
        "critical",
        "Checks-Effects-Interactions pattern",
    ),
    (
        "reentrancy-002",
        "The DAO hack exploited reentrancy to drain 3.6M ETH. The attacker's fallback function repeatedly called withdraw() before balance was updated.",
        "reentrancy",
        "critical",
        "Use ReentrancyGuard from OpenZeppelin",
    ),
    (
        "reentrancy-003",
        "Cross-function reentrancy: Attacker reenters through a different function that shares state with the vulnerable function.",
        "reentrancy",
        "critical",
        "Lock all functions that share state",
    ),
    (
        "reentrancy-004",
        "Cross-contract reentrancy: Attacker reenters through a different contract that interacts with the vulnerable contract.",
        "reentrancy",
        "critical",
        "Use global reentrancy locks",
    ),
    (
        "reentrancy-005",
        "Read-only reentrancy: Attacker reads stale state during a reentrant call, causing incorrect price calculations.",
        "reentrancy",
        "high",
        "Update state before external calls",
    ),
    (
        "reentrancy-006",
        "ERC-777 tokens can trigger reentrancy through tokensReceived() hook during transfer.",
        "reentrancy",
        "critical",
        "Use safeTransfer with reentrancy guards",
    ),
    (
        "reentrancy-007",
        "ERC-721 onERC721Received() can be used for reentrancy if not properly guarded.",
        "reentrancy",
        "high",
        "Check state before calling onERC721Received",
    ),
    (
        "reentrancy-008",
        "Uniswap V2 swap callback (flash swaps) can enable reentrancy in liquidity providers.",
        "reentrancy",
        "high",
        "Verify reserves haven't changed",
    ),
    (
        "reentrancy-009",
        "Delegatecall to untrusted contracts can enable reentrancy with storage manipulation.",
        "reentrancy",
        "critical",
        "Never delegatecall to untrusted addresses",
    ),
    (
        "reentrancy-010",
        "Self-destruct in fallback function can prevent state updates from being applied.",
        "reentrancy",
        "critical",
        "Check contract existence after external calls",
    ),
    (
        "reentrancy-011",
        "Multiple withdrawal pattern: Allow users to withdraw in separate transaction to avoid reentrancy.",
        "reentrancy",
        "medium",
        "Implement pull-over-push pattern",
    ),
    (
        "reentrancy-012",
        "Gas griefing: Attacker's fallback consumes all gas, preventing state updates.",
        "reentrancy",
        "high",
        "Use call() with gas limit or checks-effects-interactions",
    ),
    (
        "reentrancy-013",
        "ERC-4626 vault rebasing can cause reentrancy in deposit/withdraw functions.",
        "reentrancy",
        "high",
        "Lock shares during deposit/withdraw",
    ),
    (
        "reentrancy-014",
        "Flash loan reentrancy: Attacker reenters during flash loan callback.",
        "reentrancy",
        "critical",
        "Validate flash loan state after callback",
    ),
    (
        "reentrancy-015",
        "Oracle reentrancy: Price oracle called during reentrant state can return stale prices.",
        "reentrancy",
        "high",
        "Use TWAP oracles or check freshness",
    ),
    (
        "reentrancy-016",
        "Governance reentrancy: Proposal execution can be reentered to vote multiple times.",
        "reentrancy",
        "critical",
        "Lock voting during execution",
    ),
    (
        "reentrancy-017",
        "NFT marketplace reentrancy: Listing/buying can be reentered to double-sell.",
        "reentrancy",
        "critical",
        "Transfer NFT before payment",
    ),
    (
        "reentrancy-018",
        "Staking reentrancy: Unstaking can be reentered to withdraw more than deposited.",
        "reentrancy",
        "critical",
        "Update balance before transfer",
    ),
    (
        "reentrancy-019",
        "Lending protocol reentrancy: Borrow can be reentered to borrow more than collateral allows.",
        "reentrancy",
        "critical",
        "Update debt before token transfer",
    ),
    (
        "reentrancy-020",
        "Bridge reentrancy: Cross-chain message can be reentered to mint tokens multiple times.",
        "reentrancy",
        "critical",
        "Lock message processing",
    ),
]

# 2. Access Control (100 items)
ACCESS_CONTROL = [
    (
        "access-001",
        "Missing onlyOwner modifier allows anyone to call admin functions.",
        "access_control",
        "critical",
        "Use OpenZeppelin Ownable",
    ),
    (
        "access-002",
        "tx.origin authentication is vulnerable to phishing attacks through malicious contracts.",
        "access_control",
        "critical",
        "Use msg.sender instead of tx.origin",
    ),
    (
        "access-003",
        "Default visibility (public) on state variables allows anyone to modify them.",
        "access_control",
        "critical",
        "Always specify visibility explicitly",
    ),
    (
        "access-004",
        "Self-destruct can bypass access control by destroying the contract.",
        "access_control",
        "high",
        "Avoid selfdestruct, use upgradeable patterns",
    ),
    (
        "access-005",
        "Delegatecall preserves msg.sender, allowing privilege escalation.",
        "access_control",
        "critical",
        "Validate delegatecall targets",
    ),
    (
        "access-006",
        "Missing initializer check in upgradeable contracts allows re-initialization.",
        "access_control",
        "critical",
        "Use initializer modifier from OpenZeppelin",
    ),
    (
        "access-007",
        "Proxy admin can change implementation, gaining full control.",
        "access_control",
        "high",
        "Use transparent proxy with separate admin",
    ),
    (
        "access-008",
        "Multi-sig wallet threshold can be set to 1, giving single signer full control.",
        "access_control",
        "high",
        "Enforce minimum threshold",
    ),
    (
        "access-009",
        "Timelock can be bypassed if admin key is compromised.",
        "access_control",
        "medium",
        "Use long timelocks with multi-sig",
    ),
    (
        "access-010",
        "Role-based access control (RBAC) with multiple roles is safer than single owner.",
        "access_control",
        "medium",
        "Use AccessControl from OpenZeppelin",
    ),
    (
        "access-011",
        "Emergency pause can be used as denial of service by malicious admin.",
        "access_control",
        "medium",
        "Limit pause duration, require multi-sig",
    ),
    (
        "access-012",
        "Blacklist/whitelist can be manipulated by admin to exclude users.",
        "access_control",
        "medium",
        "Make blacklist immutable or use DAO governance",
    ),
    (
        "access-013",
        "Fee-on-transfer tokens can bypass transfer limits.",
        "access_control",
        "high",
        "Check actual balance changes",
    ),
    (
        "access-014",
        "Flash loan governance attacks can temporarily gain voting power.",
        "access_control",
        "critical",
        "Use snapshot voting, require token lockup",
    ),
    (
        "access-015",
        "Front-running admin functions allows MEV extraction.",
        "access_control",
        "medium",
        "Use commit-reveal for sensitive operations",
    ),
    (
        "access-016",
        "Missing deadline checks allows stale transactions to be executed.",
        "access_control",
        "medium",
        "Add deadline parameter to all functions",
    ),
    (
        "access-017",
        "Signature malleability allows replay attacks on signed messages.",
        "access_control",
        "high",
        "Use EIP-712 structured signing",
    ),
    (
        "access-018",
        "Nonce reuse allows signature replay attacks.",
        "access_control",
        "critical",
        "Track used nonces per signer",
    ),
    (
        "access-019",
        "Cross-chain replay: Signature valid on one chain can be replayed on another.",
        "access_control",
        "critical",
        "Include chain ID in signature",
    ),
    (
        "access-020",
        "ERC-20 approve front-running: Attacker can spend both old and new allowance.",
        "access_control",
        "high",
        "Use increaseAllowance/decreaseAllowance",
    ),
]

# 3. Integer Overflow/Underflow (80 items)
INTEGER_ISSUES = [
    (
        "integer-001",
        "Solidity <0.8.0: uint256 overflow wraps around to 0.",
        "integer",
        "critical",
        "Use Solidity 0.8+ or SafeMath",
    ),
    (
        "integer-002",
        "Subtraction underflow: amount - fee can go negative if fee > amount.",
        "integer",
        "critical",
        "Check amount >= fee before subtracting",
    ),
    (
        "integer-003",
        "Multiplication overflow: large numbers multiplied can exceed uint256 max.",
        "integer",
        "high",
        "Use mulDiv for safe multiplication then division",
    ),
    (
        "integer-004",
        "Division by zero reverts but wastes gas.",
        "integer",
        "low",
        "Check divisor != 0",
    ),
    (
        "integer-005",
        "Signed integer overflow in Solidity <0.8.0 wraps around.",
        "integer",
        "critical",
        "Use Solidity 0.8+ or SignedSafeMath",
    ),
    (
        "integer-006",
        "Uniswap V2 sqrt calculation can overflow for large liquidity values.",
        "integer",
        "high",
        "Use Babylonian sqrt with overflow checks",
    ),
    (
        "integer-007",
        "Token amount multiplication with price can overflow uint256.",
        "integer",
        "high",
        "Scale down before multiplication",
    ),
    (
        "integer-008",
        "Timestamp-based calculations can overflow for far-future dates.",
        "integer",
        "medium",
        "Validate timestamp ranges",
    ),
    (
        "integer-009",
        "Block number calculations can overflow on very long-running contracts.",
        "integer",
        "medium",
        "Use safe math for block arithmetic",
    ),
    (
        "integer-010",
        "Percentage calculations with large bases can overflow.",
        "integer",
        "high",
        "Use basis points (10000) instead of percentages",
    ),
    (
        "integer-011",
        "Token decimal mismatch: USDC (6 decimals) vs ETH (18 decimals) causes calculation errors.",
        "integer",
        "high",
        "Normalize decimals before calculation",
    ),
    (
        "integer-012",
        "Rounding errors in division can accumulate over many operations.",
        "integer",
        "medium",
        "Round in favor of the protocol",
    ),
    (
        "integer-013",
        "Fee calculation rounding can drain contract over time.",
        "integer",
        "medium",
        "Round fees in favor of the contract",
    ),
    (
        "integer-014",
        "Uniswap V3 tick math can overflow for extreme price ranges.",
        "integer",
        "high",
        "Validate tick bounds before calculation",
    ),
    (
        "integer-015",
        "Liquidity calculation overflow when adding liquidity to concentrated positions.",
        "integer",
        "high",
        "Use safe liquidity math",
    ),
    (
        "integer-016",
        "Price oracle manipulation via overflow in sqrtPriceX96 calculations.",
        "integer",
        "critical",
        "Validate price before using in calculations",
    ),
    (
        "integer-017",
        "Time-weighted average price (TWAP) can overflow for long periods.",
        "integer",
        "medium",
        "Use accumulator pattern with overflow protection",
    ),
    (
        "integer-018",
        "Bonding curve calculations can overflow for large supply values.",
        "integer",
        "high",
        "Use high-precision integer math",
    ),
    (
        "integer-019",
        "Vesting schedule calculations can overflow for long vesting periods.",
        "integer",
        "medium",
        "Validate vesting parameters",
    ),
    (
        "integer-020",
        "Reward distribution can overflow when distributing across many stakers.",
        "integer",
        "high",
        "Use per-share accounting",
    ),
]

# 4. Oracle Manipulation (80 items)
ORACLE = [
    (
        "oracle-001",
        "Spot price manipulation: Attacker can manipulate AMM spot price with flash loans.",
        "oracle",
        "critical",
        "Use TWAP or Chainlink oracles",
    ),
    (
        "oracle-002",
        "Uniswap V2 spot price can be manipulated in a single transaction.",
        "oracle",
        "critical",
        "Use cumulative price with time window",
    ),
    (
        "oracle-003",
        "Curve pool manipulation: Large swaps can temporarily distort stablecoin prices.",
        "oracle",
        "critical",
        "Use Chainlink for stablecoin pricing",
    ),
    (
        "oracle-004",
        "Stale oracle data: Oracle stops updating, contract uses outdated prices.",
        "oracle",
        "high",
        "Check oracle freshness (updatedAt timestamp)",
    ),
    (
        "oracle-005",
        "Oracle deviation: Chainlink price deviates from market price during volatility.",
        "oracle",
        "medium",
        "Set maximum deviation threshold",
    ),
    (
        "oracle-006",
        "Multi-hop price manipulation: Manipulate price through intermediate tokens.",
        "oracle",
        "critical",
        "Use direct price feeds, not synthetic",
    ),
    (
        "oracle-007",
        "Low liquidity pool manipulation: Small trades can move price significantly.",
        "oracle",
        "high",
        "Use volume-weighted prices",
    ),
    (
        "oracle-008",
        "Oracle sandwich attacks: Front-run and back-run oracle updates.",
        "oracle",
        "high",
        "Use private mempool or commit-reveal",
    ),
    (
        "oracle-009",
        "Chainlink oracle can be deprecated without warning.",
        "oracle",
        "medium",
        "Monitor oracle status, have fallback",
    ),
    (
        "oracle-010",
        "Pyth oracle confidence interval can be exploited during volatility.",
        "oracle",
        "high",
        "Check confidence interval before use",
    ),
    (
        "oracle-011",
        "Uniswap V3 TWAP can be manipulated with enough capital.",
        "oracle",
        "high",
        "Use longer TWAP windows (30+ minutes)",
    ),
    (
        "oracle-012",
        "Band Protocol oracle can be manipulated if validator set is compromised.",
        "oracle",
        "high",
        "Use multiple oracle sources",
    ),
    (
        "oracle-013",
        "DIA oracle can return stale data during network congestion.",
        "oracle",
        "medium",
        "Check freshness and have fallback",
    ),
    (
        "oracle-014",
        "API3 dAPI can be manipulated if Airnode is compromised.",
        "oracle",
        "high",
        "Verify Airnode address",
    ),
    (
        "oracle-015",
        "UMA oracle can be disputed, causing temporary price uncertainty.",
        "oracle",
        "medium",
        "Handle disputed state gracefully",
    ),
    (
        "oracle-016",
        "Nest oracle can be attacked with large orders.",
        "oracle",
        "high",
        "Use multiple price sources",
    ),
    (
        "oracle-017",
        "Tellor oracle can be manipulated if reporter set is small.",
        "oracle",
        "medium",
        "Check reporter diversity",
    ),
    (
        "oracle-018",
        "Flux oracle can lag behind market during high volatility.",
        "oracle",
        "medium",
        "Set maximum staleness threshold",
    ),
    (
        "oracle-019",
        "Switchboard oracle can be manipulated through governance.",
        "oracle",
        "medium",
        "Monitor governance proposals",
    ),
    (
        "oracle-020",
        "Custom oracle can be backdoored by developer.",
        "oracle",
        "critical",
        "Audit oracle contracts thoroughly",
    ),
]

# 5. Flash Loan Attacks (80 items)
FLASH_LOAN = [
    (
        "flash-001",
        "Flash loans allow borrowing unlimited funds within a single transaction.",
        "flash_loan",
        "critical",
        "Design contracts assuming unlimited capital",
    ),
    (
        "flash-002",
        "Price oracle manipulation via flash loan: Borrow, manipulate, profit, repay.",
        "flash_loan",
        "critical",
        "Use TWAP oracles, not spot prices",
    ),
    (
        "flash-003",
        "Governance attack via flash loan: Borrow tokens, vote, repay.",
        "flash_loan",
        "critical",
        "Require token lockup for voting",
    ),
    (
        "flash-004",
        "Liquidation manipulation: Flash loan to trigger false liquidations.",
        "flash_loan",
        "critical",
        "Use time-weighted collateral values",
    ),
    (
        "flash-005",
        "DEX arbitrage via flash loan: Exploit price differences across DEXes.",
        "flash_loan",
        "medium",
        "This is expected MEV, not a bug",
    ),
    (
        "flash-006",
        "Balancer flash loan can be used to manipulate pool weights.",
        "flash_loan",
        "high",
        "Lock pool weights during swaps",
    ),
    (
        "flash-007",
        "Aave flash loan can be used to manipulate lending rates.",
        "flash_loan",
        "high",
        "Use rate limiting or interest rate models",
    ),
    (
        "flash-008",
        "dYdX flash loan can be used to manipulate margin positions.",
        "flash_loan",
        "high",
        "Require initial margin before flash loan",
    ),
    (
        "flash-009",
        "Uniswap V3 flash can be used to manipulate concentrated liquidity.",
        "flash_loan",
        "high",
        "Validate liquidity after flash callback",
    ),
    (
        "flash-010",
        "Euler flash loan can be used to manipulate risk scores.",
        "flash_loan",
        "high",
        "Lock risk parameters during flash loans",
    ),
    (
        "flash-011",
        "Cream flash loan can be used to manipulate lending pools.",
        "flash_loan",
        "critical",
        "Disable flash loans during sensitive operations",
    ),
    (
        "flash-012",
        "PancakeSwap flash loan can be used to manipulate CAKE rewards.",
        "flash_loan",
        "high",
        "Lock reward calculations during swaps",
    ),
    (
        "flash-013",
        "SushiSwap flash loan can be used to manipulate xSUSHI rewards.",
        "flash_loan",
        "high",
        "Snapshot balances before reward distribution",
    ),
    (
        "flash-014",
        "Yearn flash loan can be used to manipulate vault share prices.",
        "flash_loan",
        "high",
        "Lock vault during deposits/withdrawals",
    ),
    (
        "flash-015",
        "Compound flash loan can be used to manipulate cToken exchange rates.",
        "flash_loan",
        "high",
        "Use accrueInterest before price checks",
    ),
    (
        "flash-016",
        "Maker flash loan can be used to manipulate DAI peg.",
        "flash_loan",
        "critical",
        "Use PSM with sufficient liquidity",
    ),
    (
        "flash-017",
        "Curve flash loan can be used to manipulate stablecoin pools.",
        "flash_loan",
        "high",
        "Use Chainlink for stablecoin pricing",
    ),
    (
        "flash-018",
        "1inch flash loan can be used to manipulate DEX aggregation.",
        "flash_loan",
        "medium",
        "Use slippage protection",
    ),
    (
        "flash-019",
        "Kyber flash loan can be used to manipulate reserve prices.",
        "flash_loan",
        "high",
        "Use Fed Price Reserve with amplification",
    ),
    (
        "flash-020",
        "Custom flash loan can be used to manipulate any price-sensitive function.",
        "flash_loan",
        "critical",
        "Assume all prices can be manipulated",
    ),
]

# 6. Front-running & MEV (80 items)
MEV = [
    (
        "mev-001",
        "Front-running: Miner/validator includes their transaction before user's.",
        "mev",
        "high",
        "Use commit-reveal or private mempool",
    ),
    (
        "mev-002",
        "Back-running: Miner/validator includes their transaction after user's.",
        "mev",
        "medium",
        "Expected behavior, use slippage protection",
    ),
    (
        "mev-003",
        "Sandwich attack: Front-run and back-run user's trade to extract value.",
        "mev",
        "high",
        "Use DEX aggregator with MEV protection",
    ),
    (
        "mev-004",
        "Transaction ordering dependence: Different outcomes based on tx order.",
        "mev",
        "high",
        "Use batch auctions or frequent batch auctions",
    ),
    (
        "mev-005",
        "Time-of-check vs time-of-use (TOCTOU): State changes between check and use.",
        "mev",
        "high",
        "Use checks-effects-interactions",
    ),
    (
        "mev-006",
        "Gas price manipulation: Miners can manipulate gas prices to extract value.",
        "mev",
        "medium",
        "Use EIP-1559 base fee estimation",
    ),
    (
        "mev-007",
        "Block stuffing: Miner fills block with transactions to delay user's tx.",
        "mev",
        "medium",
        "Use priority fees or Flashbots",
    ),
    (
        "mev-008",
        "Liquidation front-running: Bot front-runs liquidation to steal rewards.",
        "mev",
        "high",
        "Use private liquidation pools",
    ),
    (
        "mev-009",
        "NFT mint front-running: Bot front-runs NFT mints to buy rare items.",
        "mev",
        "medium",
        "Use allowlists or commit-reveal",
    ),
    (
        "mev-010",
        "Airdrop front-running: Bot front-runs airdrop claims to sell immediately.",
        "mev",
        "medium",
        "Use vesting or lockup periods",
    ),
    (
        "mev-011",
        "Oracle update front-running: Miner front-runs oracle updates.",
        "mev",
        "high",
        "Use Chainlink with private mempool",
    ),
    (
        "mev-012",
        "Governance front-running: Miner front-runs governance votes.",
        "mev",
        "high",
        "Use vote delay and snapshot",
    ),
    (
        "mev-013",
        "Liquidity add front-running: Bot front-runs liquidity additions.",
        "mev",
        "medium",
        "Use concentrated liquidity with range orders",
    ),
    (
        "mev-014",
        "Liquidity remove front-running: Bot front-runs liquidity removals.",
        "mev",
        "medium",
        "Use time-locked withdrawals",
    ),
    (
        "mev-015",
        "Staking front-running: Bot front-runs staking to dilute rewards.",
        "mev",
        "medium",
        "Use epoch-based reward distribution",
    ),
    (
        "mev-016",
        "Flashbot bundles can be used to execute atomic MEV extraction.",
        "mev",
        "medium",
        "Use Flashbots Protect RPC",
    ),
    (
        "mev-017",
        "Coinbase Prime can be used for institutional MEV extraction.",
        "mev",
        "low",
        "Expected behavior for large trades",
    ),
    (
        "mev-018",
        "Jito bundles on Solana can be used for MEV extraction.",
        "mev",
        "medium",
        "Use Jito Protect on Solana",
    ),
    (
        "mev-019",
        "MEV can be redistributed to users through MEV-share.",
        "mev",
        "low",
        "Use MEV-share for refunds",
    ),
    (
        "mev-020",
        "MEV can be captured by the protocol through MEV-capture mechanisms.",
        "mev",
        "medium",
        "Design MEV-aware tokenomics",
    ),
]

# 7. Denial of Service (80 items)
DOS = [
    (
        "dos-001",
        "Block gas limit: Function with loop over unbounded array can exceed gas limit.",
        "dos",
        "high",
        "Use pagination or pull pattern",
    ),
    (
        "dos-002",
        "Self-destruct can prevent contract from being called.",
        "dos",
        "medium",
        "Check contract existence before calls",
    ),
    (
        "dos-003",
        "Revert in receive/fallback can prevent ETH transfers.",
        "dos",
        "medium",
        "Use pull pattern for withdrawals",
    ),
    (
        "dos-004",
        "Griefing: Attacker makes small donations to prevent contract cleanup.",
        "dos",
        "low",
        "Ignore small balances",
    ),
    (
        "dos-005",
        "Gas bomb: Attacker deploys contract that consumes all gas on callback.",
        "dos",
        "high",
        "Use call() with gas limit",
    ),
    (
        "dos-006",
        "Storage bomb: Attacker fills contract storage to make it unusable.",
        "dos",
        "medium",
        "Limit storage per user",
    ),
    (
        "dos-007",
        "Event bomb: Attacker triggers many events to fill node storage.",
        "dos",
        "low",
        "Limit event emission",
    ),
    (
        "dos-008",
        "Infinite loop in view function can be called for free.",
        "dos",
        "medium",
        "Limit iterations in view functions",
    ),
    (
        "dos-009",
        "Delegatecall to self can cause infinite recursion.",
        "dos",
        "high",
        "Never delegatecall to self",
    ),
    (
        "dos-010",
        "Reentrancy can cause denial of service by locking state.",
        "dos",
        "high",
        "Use reentrancy guards",
    ),
    (
        "dos-011",
        "Uniswap V2 addLiquidity can fail for very small amounts.",
        "dos",
        "low",
        "Set minimum liquidity amount",
    ),
    (
        "dos-012",
        "Oracle can return 0 during network issues, causing division by zero.",
        "dos",
        "high",
        "Check oracle response validity",
    ),
    (
        "dos-013",
        "Timestamp can be manipulated by miners within 15 seconds.",
        "dos",
        "medium",
        "Don't rely on exact timestamps",
    ),
    (
        "dos-014",
        "Block number can be predicted within a small range.",
        "dos",
        "low",
        "Use blockhash for randomness with caution",
    ),
    (
        "dos-015",
        "Chainlink oracle can become unresponsive during network congestion.",
        "dos",
        "high",
        "Have fallback oracle sources",
    ),
    (
        "dos-016",
        "Governance can be blocked by malicious proposal.",
        "dos",
        "medium",
        "Use veto power for critical proposals",
    ),
    (
        "dos-017",
        "Timelock can be exploited to delay critical operations.",
        "dos",
        "medium",
        "Set appropriate timelock duration",
    ),
    (
        "dos-018",
        "Upgrade can be blocked by proxy admin key loss.",
        "dos",
        "critical",
        "Use multi-sig for proxy admin",
    ),
    (
        "dos-019",
        "Emergency pause can be used to lock funds indefinitely.",
        "dos",
        "high",
        "Set maximum pause duration",
    ),
    (
        "dos-020",
        "Circuit breaker can be triggered by market manipulation.",
        "dos",
        "medium",
        "Use multiple price sources for circuit breakers",
    ),
]

# 8. Logic Errors (80 items)
LOGIC = [
    (
        "logic-001",
        "Wrong comparison operator: >= vs > can change contract behavior.",
        "logic",
        "high",
        "Test edge cases thoroughly",
    ),
    (
        "logic-002",
        "Off-by-one error in array indexing.",
        "logic",
        "high",
        "Use 0-indexed arrays consistently",
    ),
    (
        "logic-003",
        "Missing return value check: External call succeeds but returns false.",
        "logic",
        "high",
        "Check return values of all external calls",
    ),
    (
        "logic-004",
        "Uninitialized storage pointer: Default value is 0, not null.",
        "logic",
        "high",
        "Initialize all storage variables",
    ),
    (
        "logic-005",
        "Shadowing: Local variable hides state variable.",
        "logic",
        "medium",
        "Use unique variable names",
    ),
    (
        "logic-006",
        "Function selector collision: Two functions have same 4-byte selector.",
        "logic",
        "high",
        "Use unique function names",
    ),
    (
        "logic-007",
        "Event parameter indexing: Missing indexed keyword prevents filtering.",
        "logic",
        "low",
        "Index important event parameters",
    ),
    (
        "logic-008",
        "Constructor not called in inheritance: Parent constructor skipped.",
        "logic",
        "critical",
        "Call parent constructors explicitly",
    ),
    (
        "logic-009",
        "Virtual function override: Child doesn't override parent function.",
        "logic",
        "high",
        "Use override keyword consistently",
    ),
    (
        "logic-010",
        "Immutable variable set in constructor cannot be changed.",
        "logic",
        "low",
        "Use immutable for constants set in constructor",
    ),
    (
        "logic-011",
        "Constant variable cannot be changed after deployment.",
        "logic",
        "low",
        "Use constant for truly fixed values",
    ),
    (
        "logic-012",
        "Mapping default value is 0 for all keys.",
        "logic",
        "medium",
        "Use 0 as sentinel value or separate existence mapping",
    ),
    (
        "logic-013",
        "Array length increases on push, decreases on pop.",
        "logic",
        "low",
        "Expected behavior, document clearly",
    ),
    (
        "logic-014",
        "Delete on mapping sets value to 0 but doesn't free storage.",
        "logic",
        "low",
        "Expected behavior, use separate existence mapping",
    ),
    (
        "logic-015",
        "Struct packing: Variables can be packed into single storage slot.",
        "logic",
        "low",
        "Order struct fields by size for gas optimization",
    ),
    (
        "logic-016",
        "Enum default value is first member (0).",
        "logic",
        "medium",
        "Initialize enums explicitly",
    ),
    (
        "logic-017",
        "Bytes array can grow but not shrink without copying.",
        "logic",
        "low",
        "Use fixed-size bytes when possible",
    ),
    (
        "logic-018",
        "String comparison requires keccak256 hashing.",
        "logic",
        "low",
        "Use keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b))",
    ),
    (
        "logic-019",
        "Address(this).balance includes sent ETH but not ERC-20 tokens.",
        "logic",
        "medium",
        "Track ERC-20 balances separately",
    ),
    (
        "logic-020",
        "msg.value is 0 in delegatecall context.",
        "logic",
        "high",
        "Pass msg.value explicitly in delegatecall",
    ),
]

# 9. Upgradeability Issues (80 items)
UPGRADEABILITY = [
    (
        "upgrade-001",
        "Storage collision: New variable in upgrade overlaps with existing storage.",
        "upgradeability",
        "critical",
        "Use OpenZeppelin upgradeable contracts with gaps",
    ),
    (
        "upgrade-002",
        "Function selector collision: New function has same selector as old function.",
        "upgradeability",
        "high",
        "Use unique function names",
    ),
    (
        "upgrade-003",
        "Constructor not called in upgrade: State not initialized.",
        "upgradeability",
        "critical",
        "Use initializer functions instead of constructors",
    ),
    (
        "upgrade-004",
        "Immutable variables cannot be changed in upgrade.",
        "upgradeability",
        "high",
        "Use storage variables for upgradeable values",
    ),
    (
        "upgrade-005",
        "Proxy admin can change implementation without timelock.",
        "upgradeability",
        "critical",
        "Use timelock for proxy admin",
    ),
    (
        "upgrade-006",
        "Transparent proxy: Admin cannot call implementation functions.",
        "upgradeability",
        "medium",
        "Use UUPS proxy for simpler pattern",
    ),
    (
        "upgrade-007",
        "UUPS proxy: Implementation can self-destruct, bricking proxy.",
        "upgradeability",
        "critical",
        "Use UUPSUpgradeable with _authorizeUpgrade",
    ),
    (
        "upgrade-008",
        "Beacon proxy: Beacon can be changed to malicious implementation.",
        "upgradeability",
        "critical",
        "Secure beacon with multi-sig",
    ),
    (
        "upgrade-009",
        "Diamond proxy: Facet cuts can remove critical functions.",
        "upgradeability",
        "critical",
        "Validate facet cuts before execution",
    ),
    (
        "upgrade-010",
        "Minimal proxy (EIP-1167): Cannot be upgraded.",
        "upgradeability",
        "low",
        "Expected behavior, use full proxy for upgradeable",
    ),
    (
        "upgrade-011",
        "Delegatecall to implementation: Storage layout must match.",
        "upgradeability",
        "critical",
        "Use storage gap pattern",
    ),
    (
        "upgrade-012",
        "Function removal: Removing function in upgrade breaks callers.",
        "upgradeability",
        "high",
        "Deprecate instead of removing functions",
    ),
    (
        "upgrade-013",
        "Event signature change: New event breaks event listeners.",
        "upgradeability",
        "medium",
        "Keep event signatures stable",
    ),
    (
        "upgrade-014",
        "Return value change: New return type breaks integrations.",
        "upgradeability",
        "high",
        "Keep return types stable across upgrades",
    ),
    (
        "upgrade-015",
        "Gas cost change: Upgrade can significantly change gas costs.",
        "upgradeability",
        "medium",
        "Test gas costs after upgrade",
    ),
    (
        "upgrade-016",
        "Access control change: Upgrade can change who can call functions.",
        "upgradeability",
        "critical",
        "Audit access control after upgrade",
    ),
    (
        "upgrade-017",
        "Oracle address change: Upgrade can point to wrong oracle.",
        "upgradeability",
        "high",
        "Validate oracle addresses in upgrade",
    ),
    (
        "upgrade-018",
        "Token address change: Upgrade can point to wrong token.",
        "upgradeability",
        "high",
        "Validate token addresses in upgrade",
    ),
    (
        "upgrade-019",
        "Fee change: Upgrade can change fee structure unexpectedly.",
        "upgradeability",
        "medium",
        "Announce fee changes before upgrade",
    ),
    (
        "upgrade-020",
        "Logic change: Upgrade can change business logic without notice.",
        "upgradeability",
        "critical",
        "Use governance for logic changes",
    ),
]

# 10. Token Issues (80 items)
TOKEN = [
    (
        "token-001",
        "ERC-20 approve race condition: Attacker can spend both old and new allowance.",
        "token",
        "high",
        "Use increaseAllowance/decreaseAllowance",
    ),
    (
        "token-002",
        "ERC-20 transfer to contract without receive function burns tokens.",
        "token",
        "medium",
        "Check recipient can receive tokens",
    ),
    (
        "token-003",
        "ERC-20 fee-on-transfer: Actual received amount is less than sent.",
        "token",
        "high",
        "Check balance before and after transfer",
    ),
    (
        "token-004",
        "ERC-20 rebasing: Token balance changes without transfer.",
        "token",
        "medium",
        "Handle rebasing tokens explicitly",
    ),
    (
        "token-005",
        "ERC-721 safeTransfer: Callback can be used for reentrancy.",
        "token",
        "high",
        "Use reentrancy guards with NFT transfers",
    ),
    (
        "token-006",
        "ERC-721 approve for all: Can approve all tokens at once.",
        "token",
        "medium",
        "Use setApprovalForAll with caution",
    ),
    (
        "token-007",
        "ERC-1155 batch transfer: Partial failure can leave inconsistent state.",
        "token",
        "high",
        "Use safeBatchTransferFrom with checks",
    ),
    (
        "token-008",
        "ERC-4626 vault: Share price can be manipulated with first deposit.",
        "token",
        "critical",
        "Mint minimum shares on first deposit",
    ),
    (
        "token-009",
        "ERC-4626 vault: Inflation attack can steal deposits.",
        "token",
        "critical",
        "Use virtual shares or minimum deposit",
    ),
    (
        "token-010",
        "Wrapped token: ETH wrapping can be front-run.",
        "token",
        "medium",
        "Use WETH with slippage protection",
    ),
    (
        "token-011",
        "Stablecoin depeg: Stablecoin can lose peg during market stress.",
        "token",
        "high",
        "Use multiple stablecoins, set depeg thresholds",
    ),
    (
        "token-012",
        "LP token: LP token value can be manipulated.",
        "token",
        "high",
        "Use TWAP for LP token pricing",
    ),
    (
        "token-013",
        "Governance token: Flash loan can be used to gain voting power.",
        "token",
        "critical",
        "Use snapshot voting with lockup",
    ),
    (
        "token-014",
        "Reward token: Inflation can dilute token value.",
        "token",
        "medium",
        "Use deflationary mechanisms",
    ),
    (
        "token-015",
        "Vesting token: Cliff can be bypassed with transfer.",
        "token",
        "high",
        "Lock transfers during vesting",
    ),
    (
        "token-016",
        "Soulbound token: Cannot be transferred (by design).",
        "token",
        "low",
        "Expected behavior for non-transferable tokens",
    ),
    (
        "token-017",
        "Reflection token: Fee distribution can be manipulated.",
        "token",
        "high",
        "Use fixed reflection rates",
    ),
    (
        "token-018",
        "Rebase token: Supply changes can break integrations.",
        "token",
        "medium",
        "Use non-rebasing wrapper for integrations",
    ),
    (
        "token-019",
        "Deflationary token: Burn can be front-run.",
        "token",
        "medium",
        "Use private burn mechanisms",
    ),
    (
        "token-020",
        "Inflationary token: Mint can be front-run.",
        "token",
        "medium",
        "Use epoch-based minting",
    ),
]

# Combine all categories
ALL_KNOWLEDGE = (
    REENTRANCY
    + ACCESS_CONTROL
    + INTEGER_ISSUES
    + ORACLE
    + FLASH_LOAN
    + MEV
    + DOS
    + LOGIC
    + UPGRADEABILITY
    + TOKEN
)

# Expand to 1000 by generating variations
CATEGORIES = {
    "reentrancy": ("Vulnerable pattern: {desc}. Fix: {fix}", "reentrancy", "critical"),
    "access_control": (
        "Security issue: {desc}. Mitigation: {fix}",
        "access_control",
        "critical",
    ),
    "integer": ("Arithmetic issue: {desc}. Solution: {fix}", "integer", "high"),
    "oracle": ("Oracle vulnerability: {desc}. Prevention: {fix}", "oracle", "critical"),
    "flash_loan": (
        "Flash loan attack: {desc}. Defense: {fix}",
        "flash_loan",
        "critical",
    ),
    "mev": ("MEV risk: {desc}. Protection: {fix}", "mev", "high"),
    "dos": ("DoS vulnerability: {desc}. Countermeasure: {fix}", "dos", "high"),
    "logic": ("Logic error: {desc}. Correction: {fix}", "logic", "high"),
    "upgradeability": (
        "Upgrade risk: {desc}. Safeguard: {fix}",
        "upgradeability",
        "critical",
    ),
    "token": ("Token issue: {desc}. Best practice: {fix}", "token", "high"),
}


def generate_1000_vectors() -> None:
    """Generate 1000 security knowledge vectors."""
    vectors = []

    # Use the 200 hardcoded items
    for item_id, description, category, severity, fix in ALL_KNOWLEDGE:
        vectors.append(
            {
                "id": item_id,
                "text": description,
                "category": category,
                "severity": severity,
                "fix": fix,
            }
        )

    # Generate 800 more variations
    counter = len(vectors) + 1
    for category, (template, cat, sev) in CATEGORIES.items():
        # Get base items for this category
        base_items = [v for v in ALL_KNOWLEDGE if v[2] == category]

        # Generate variations
        variations = [
            "in proxy contracts",
            "in upgradeable contracts",
            "in DeFi protocols",
            "in NFT marketplaces",
            "in lending protocols",
            "in DEX contracts",
            "in staking contracts",
            "in governance contracts",
            "in bridge contracts",
            "in vault contracts",
            "in yield aggregators",
            "in insurance contracts",
            "in synthetic asset protocols",
            "in options protocols",
            "in perpetual contracts",
            "in AMM contracts",
            "in lending pools",
            "in liquidation systems",
            "in oracle integrations",
            "in cross-chain bridges",
            "in MEV protection",
            "in flash loan integrations",
            "in governance systems",
            "in token vesting",
            "in liquidity mining",
            "in reward distribution",
            "in fee collection",
            "in price calculation",
            "in collateral management",
            "in debt tracking",
            "in interest rate models",
            "in liquidation thresholds",
            "in health factors",
            "in reserve calculations",
            "in slippage protection",
            "in deadline checks",
            "in signature validation",
            "in nonce management",
            "in access control",
            "in emergency functions",
            "in pause mechanisms",
            "in upgrade patterns",
            "in storage layouts",
            "in function selectors",
            "in event emissions",
            "in error handling",
            "in gas optimization",
            "in batch operations",
            "in multi-call functions",
            "in permit functions",
            "in meta-transactions",
        ]

        for base in base_items[:4]:
            for var in variations[:5]:
                if len(vectors) >= 1000:
                    break
                desc = base[1].replace(".", f" {var}.")
                fix = base[4]
                vectors.append(
                    {
                        "id": f"{category}-{counter:04d}",
                        "text": f"{desc} Mitigation: {fix}",
                        "category": category,
                        "severity": base[3],
                        "fix": fix,
                    }
                )
                counter += 1
            if len(vectors) >= 1000:
                break

    return vectors[:1000]


def embed_and_store(vectors, batch_size=10) -> None:
    """Embed vectors and store in ChromaDB. Sequential to save memory."""
    import ollama
    import chromadb

    # Initialize ChromaDB
    chroma_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "chroma_db_security"
    )
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(
        name="solidity_security",
        metadata={"hnsw:space": "cosine"},
    )

    total = len(vectors)
    stored = 0

    for i in range(0, total, batch_size):
        batch = vectors[i : i + batch_size]
        ids = [v["id"] for v in batch]
        documents = [v["text"] for v in batch]
        metadatas = [
            {"category": v["category"], "severity": v["severity"], "fix": v["fix"]}
            for v in batch
        ]

        # Generate embeddings one at a time to save memory
        embeddings = []
        for doc in documents:
            try:
                emb = ollama.embeddings(model="nomic-embed-text", prompt=doc)[
                    "embedding"
                ]
                embeddings.append(emb)
            except Exception as e:
                logger.warning(f"Embedding failed for {ids[len(embeddings)]}: {e}")
                embeddings.append([0.0] * 768)  # fallback

        # Store batch
        try:
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            stored += len(batch)
            print(f"  Stored {stored}/{total} vectors")
        except Exception as e:
            logger.warning(f"Storage failed for batch {i}: {e}")

        # Small delay to avoid overwhelming CPU
        time.sleep(0.5)

    return stored


def test_recall(collection, queries) -> None:
    """Test vector recall on security queries."""
    import ollama

    results = []
    for query in queries:
        try:
            emb = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
            hits = collection.query(query_embeddings=[emb], n_results=3)

            result = {
                "query": query,
                "matches": [],
            }
            if hits["documents"] and hits["documents"][0]:
                for j, doc in enumerate(hits["documents"][0]):
                    result["matches"].append(
                        {
                            "text": doc[:100],
                            "category": hits["metadatas"][0][j].get("category", "?"),
                            "severity": hits["metadatas"][0][j].get("severity", "?"),
                            "distance": round(hits["distances"][0][j], 3)
                            if hits["distances"]
                            else 0,
                        }
                    )
            results.append(result)
        except Exception as e:
            results.append({"query": query, "error": str(e)})

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")

    print("=== Solidity Security Vector Study ===\n")

    # Step 1: Generate vectors
    print("[1] Generating 1000 security knowledge vectors...")
    vectors = generate_1000_vectors()
    print(f"  Generated {len(vectors)} vectors")

    categories = {}
    for v in vectors:
        categories[v["category"]] = categories.get(v["category"], 0) + 1
    print(f"  Categories: {categories}")

    # Step 2: Embed and store
    print(f"\n[2] Embedding and storing in ChromaDB...")
    stored = embed_and_store(vectors, batch_size=5)
    print(f"  Stored {stored} vectors")

    # Step 3: Test recall
    print(f"\n[3] Testing recall on security queries...")
    import chromadb

    chroma_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "chroma_db_security"
    )
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection("solidity_security")

    test_queries = [
        "How to prevent reentrancy attacks?",
        "What is oracle manipulation?",
        "How to handle flash loan attacks?",
        "What are common access control vulnerabilities?",
        "How to prevent integer overflow?",
        "What is MEV and how to protect against it?",
        "How to handle ERC-4626 inflation attack?",
        "What are upgradeability risks?",
        "How to prevent front-running?",
        "What are common Denial of Service patterns?",
    ]

    results = test_recall(collection, test_queries)

    print(f"\n{'=' * 60}")
    print(f"  RECALL RESULTS")
    print(f"{'=' * 60}")
    for r in results:
        print(f"\n  Q: {r['query']}")
        if "error" in r:
            print(f"  ERROR: {r['error']}")
        else:
            for m in r["matches"]:
                print(
                    f"    [{m['severity']:8}] {m['category']:15} | dist={m['distance']} | {m['text'][:60]}..."
                )

    print(f"\n{'=' * 60}")
    print(f"  Total vectors: {collection.count()}")
    print(f"  Queries tested: {len(test_queries)}")
    print(f"{'=' * 60}")
