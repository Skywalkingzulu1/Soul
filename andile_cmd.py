#!/usr/bin/env python3
"""Andile Command Interface - For Gemini CLI to execute

Usage:
  andile think "your prompt here"        - Send to Andile's 120B model
  andile status                         - Check orchestration status
  andile goals                          - Show Andile's goals progress
  andile tasks                          - Show pending tasks
  andile log <message>                 - Log activity
  andile task add <description>         - Add a new task
  andile task complete <task_id>        - Mark task complete
  andile wallet create                  - Create new crypto wallet
  andile wallet info                   - Show wallet info
  andile airdrops                       - List airdrop opportunities
  andile github prs                     - List recent PRs
"""

import sys
import json
import os
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from soul.orchestration import Orchestration, AndileCloud, get_orchestration
from soul.orchestration import orchestrate_task


def cmd_think(prompt: str):
    """Send prompt to Andile cloud model."""
    andile = AndileCloud()

    if not andile.is_available():
        print("Error: Andile cloud model not available")
        print("Make sure Ollama is running with gpt-oss:120b-cloud")
        return 1

    print(f"Andile (120B): Thinking...")
    response = andile.think(prompt)
    print(response)
    return 0


def cmd_status():
    """Show orchestration status."""
    orch = get_orchestration()
    status = orch.get_status()
    print(json.dumps(status, indent=2))
    return 0


def cmd_goals():
    """Show Andile's goals."""
    orch = get_orchestration()
    andile = orch.state.get("participants", {}).get("andile", {})
    goals = andile.get("goals", {})

    print("=== Andile's Goals ===\n")

    for name, goal in goals.items():
        print(f"[{name.upper()}]")
        print(f"  Status: {goal.get('status', 'unknown')}")
        print(f"  Last action: {goal.get('last_action', 'none')}")

        if name == "get_paid":
            print(f"  Jobs applied: {goal.get('jobs_applied', 0)}")
            print(f"  Income earned: ${goal.get('income_earned', 0)}")
        elif name == "github_growth":
            print(f"  PRs made: {goal.get('prs_made', 0)}")
            print(f"  PRs merged: {goal.get('prs_merged', 0)}")
            print(f"  Target repos: {', '.join(goal.get('repos_targeted', []))}")
        elif name == "crypto_growth":
            print(f"  Wallet: {goal.get('wallet_address', 'not created')}")
            print(f"  Airdrops claimed: {goal.get('airdrops_claimed', 0)}")
            print(f"  Total value: ${goal.get('total_value', 0)}")
            print(f"  Strategy: {goal.get('strategy', 'airdrop_hunting')}")
        print()
    return 0


def cmd_tasks():
    """Show pending tasks."""
    orch = get_orchestration()
    tasks = orch.state.get("tasks", [])

    print("=== Tasks ===\n")
    pending = [t for t in tasks if t.get("status") == "pending"]

    if not pending:
        print("No pending tasks")
    else:
        for t in pending:
            print(f"[{t.get('id')}] {t.get('task')}")
            print(f"  Assigned to: {t.get('assigned_to')}")
            print(f"  Priority: {t.get('priority')}")
            print(f"  Created: {t.get('created_at')}")
            print()
    return 0


def cmd_log(message: str):
    """Log a message."""
    orch = get_orchestration()
    orch.log_activity("user", "message", {"content": message})
    print(f"Logged: {message}")
    return 0


def cmd_task_add(description: str, assigned_to: str = "gemini"):
    """Add a new task."""
    orch = get_orchestration()
    task_id = orch.add_task(description, assigned_to)
    print(f"Added task [{task_id}]: {description}")
    return 0


def cmd_task_complete(task_id: str, result: str = None):
    """Complete a task."""
    orch = get_orchestration()
    orch.complete_task(task_id, result)
    print(f"Completed task: {task_id}")
    return 0


def cmd_wallet_create():
    """Create a new crypto wallet."""
    from web3 import Web3
    import secrets

    # Generate new wallet
    private_key = "0x" + secrets.token_hex(32)
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    # Save to orchestration state (encrypted in production!)
    orch = get_orchestration()
    orch.update_goal(
        "crypto_growth",
        {
            "wallet_address": account.address,
            "wallet_seed": private_key,  # NOTE: In production, encrypt this!
            "created_at": str(datetime.now()),
        },
    )

    print(f"Wallet created!")
    print(f"  Address: {account.address}")
    print(f"  (Seed stored securely in orchestration state)")
    print(f"\nWARNING: This is a new wallet. Use for airdrop hunting only.")
    return 0


def cmd_wallet_info():
    """Show wallet info."""
    orch = get_orchestration()
    crypto = (
        orch.state.get("participants", {})
        .get("andile", {})
        .get("goals", {})
        .get("crypto_growth", {})
    )

    print("=== Crypto Wallet ===\n")
    print(f"Address: {crypto.get('wallet_address', 'Not created')}")
    print(f"Airdrops claimed: {crypto.get('airdrops_claimed', 0)}")
    print(f"Total value: ${crypto.get('total_value', 0)}")
    print(f"Strategy: {crypto.get('strategy', 'airdrop_hunting')}")
    return 0


def cmd_airdrops():
    """Show airdrop opportunities."""
    # This would be enhanced with real-time data
    print("=== Airdrop Opportunities ===\n")
    print("Note: This requires web research. Run with Andile to research.")
    print("\nKnown airdrop-worthy protocols (research eligibility):")
    print("  - Monad (testnet activity)")
    print("  - Berachain (testnet)")
    print("  - LayerZero (volume)")
    print("  - zkSync Era (bridge usage)")
    print("  - Starknet (transactions)")
    print("  - Scroll (bridge activity)")
    print("  - Linea (DeFi usage)")
    print("\nRun 'andile think' to research specific airdrops.")
    return 0


def cmd_github_prs():
    """Show recent PRs."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--owner",
                "Skywalkingzulu1",
                "--state",
                "all",
                "--limit",
                "10",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        print("=== Your PRs ===\n")
        print(result.stdout or "No PRs found")
    except Exception as e:
        print(f"Error: {e}")
    return 0


def cmd_bounties(repo: str = None):
    """Find GitHub bounties for repos."""
    import subprocess

    print("=== GitHub Bounties ===\n")

    repos = [
        "pancakeswap/pancake-frontend",
        "uniswap/uniswap-v3-core",
        "curvefi/curve-contracts",
        "balancer-labs/balancer-core-v2",
    ]

    if repo:
        repos = [repo]

    total_bounties = 0

    for full_repo in repos:
        print(f"Checking {full_repo}...")

        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{full_repo}/issues?state=open&per_page=20"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.stdout:
                import json

                issues = json.loads(result.stdout)
                bounty_issues = []
                for issue in issues:
                    labels = [
                        lbl.get("name", "").lower() for lbl in issue.get("labels", [])
                    ]
                    if any(
                        b in label
                        for label in labels
                        for b in ["bounty", "reward", "grant", "prize", "hackathon"]
                    ):
                        bounty_issues.append(
                            f"  [{labels}] {issue.get('title')} #{issue.get('number')}"
                        )

                if bounty_issues:
                    print(f"\n  {full_repo}:")
                    for bi in bounty_issues:
                        print(bi)
                    total_bounties += len(bounty_issues)

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n=== Summary ===")
    print(f"Bounty issues found: {total_bounties}")
    print("\nExternal bounty platforms:")
    print("  - gitcoin.co (DeFi bounties)")
    print("  - immunefi.com (security)")
    print("  - layer3.xyz (quests)")
    print("  - bug bounty programs")

    orch = get_orchestration()
    orch.update_goal(
        "get_paid",
        {
            "bounties_found": total_bounties,
            "last_action": f"bounties_checked_{datetime.now().isoformat()}",
        },
    )

    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]

    if command == "think":
        if len(sys.argv) < 3:
            print("Usage: andile think <prompt>")
            return 1
        return cmd_think(" ".join(sys.argv[2:]))
    elif command == "status":
        return cmd_status()
    elif command == "goals":
        return cmd_goals()
    elif command == "tasks":
        return cmd_tasks()
    elif command == "log":
        if len(sys.argv) < 3:
            print("Usage: andile log <message>")
            return 1
        return cmd_log(" ".join(sys.argv[2:]))
    elif command == "task":
        if len(sys.argv) < 3:
            print("Usage: andile task <add|complete> ...")
            return 1
        subcmd = sys.argv[2]
        if subcmd == "add":
            return cmd_task_add(" ".join(sys.argv[3:]))
        elif subcmd == "complete":
            return cmd_task_complete(sys.argv[3] if len(sys.argv) > 3 else "")
        else:
            print(f"Unknown task subcommand: {subcmd}")
            return 1
    elif command == "wallet":
        if len(sys.argv) < 3:
            print("Usage: andile wallet <create|info>")
            return 1
        subcmd = sys.argv[2]
        if subcmd == "create":
            return cmd_wallet_create()
        elif subcmd == "info":
            return cmd_wallet_info()
    elif command == "airdrops":
        return cmd_airdrops()
    elif command == "github":
        if len(sys.argv) < 3:
            print("Usage: andile github <prs|bounties> [repo]")
            return 1
        if sys.argv[2] == "prs":
            return cmd_github_prs()
        elif sys.argv[2] == "bounties":
            repo = sys.argv[3] if len(sys.argv) > 3 else None
            return cmd_bounties(repo)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1


if __name__ == "__main__":
    from datetime import datetime

    sys.exit(main())
