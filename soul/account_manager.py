"""Andile Account System - Self-service account creation

Enables Andile to:
1. Create accounts on various platforms automatically
2. Manage credentials securely
3. Track all accounts owned by Andile
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "knowledge", "accounts.json"
)


@dataclass
class Account:
    """Represents an account."""

    platform: str
    username: str
    email: str
    account_id: Optional[str]
    created_at: str
    status: str  # "active", "pending", "suspended"
    capabilities: List[str]  # what the account can do
    verification_level: str  # "none", "email", "phone", "kyc"


class AccountManager:
    """Manages Andile's accounts."""

    def __init__(self):
        self.accounts = self._load_accounts()
        self.platforms = self._get_supported_platforms()

    def _load_accounts(self) -> List[Account]:
        """Load accounts from file."""
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, "r") as f:
                data = json.load(f)
                return [Account(**a) for a in data.get("accounts", [])]
        return []

    def _save_accounts(self):
        """Save accounts to file."""
        data = {
            "accounts": [asdict(a) for a in self.accounts],
            "last_updated": datetime.now().isoformat(),
        }
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def _get_supported_platforms(self) -> Dict:
        """Get supported platforms for account creation."""
        return {
            "github": {
                "name": "GitHub",
                "url": "https://github.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "gitlab": {
                "name": "GitLab",
                "url": "https://gitlab.com/users/sign_up",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "docker": {
                "name": "Docker Hub",
                "url": "https://hub.docker.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "railway": {
                "name": "Railway",
                "url": "https://railway.app/signup",
                "email_required": True,
                "phone_required": True,
                "requires_proxy": False,
                "automation": "browser",
            },
            "cloudflare": {
                "name": "Cloudflare",
                "url": "https://dash.cloudflare.com/signup",
                "email_required": True,
                "phone_required": True,
                "requires_proxy": False,
                "automation": "browser",
            },
            "fly_io": {
                "name": "Fly.io",
                "url": "https://fly.io/signup",
                "email_required": True,
                "phone_required": True,
                "requires_proxy": False,
                "automation": "browser",
            },
            "oracle": {
                "name": "Oracle Cloud",
                "url": "https://signup.cloud.oracle.com/",
                "email_required": True,
                "phone_required": True,
                "requires_proxy": False,
                "automation": "browser",
            },
            "render": {
                "name": "Render",
                "url": "https://render.com/register",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "vercel": {
                "name": "Vercel",
                "url": "https://vercel.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "netlify": {
                "name": "Netlify",
                "url": "https://app.netlify.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "replit": {
                "name": "Replit",
                "url": "https://replit.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "glitch": {
                "name": "Glitch",
                "url": "https://glitch.com/signup",
                "email_required": True,
                "phone_required": False,
                "requires_proxy": False,
                "automation": "browser",
            },
            "crypto_exchanges": {
                "name": "Crypto Exchanges (CEX)",
                "platforms": ["binance", "bybit", "okx", "kucoin"],
                "note": "Most require KYC for full features",
            },
            "defi": {
                "name": "DeFi Protocols",
                "platforms": ["uniswap", "aerodrome", "curve"],
                "note": "Wallet-based, no account needed",
            },
        }

    def add_account(
        self,
        platform: str,
        username: str,
        email: str = None,
        account_id: str = None,
        capabilities: List[str] = None,
    ) -> Account:
        """Add a new account."""
        # Check if already exists
        for acc in self.accounts:
            if acc.platform == platform and acc.username == username:
                return acc

        account = Account(
            platform=platform,
            username=username,
            email=email or "andilexmchunu@gmail.com",
            account_id=account_id,
            created_at=datetime.now().isoformat(),
            status="active",
            capabilities=capabilities or [],
            verification_level="email",
        )
        self.accounts.append(account)
        self._save_accounts()
        return account

    def get_accounts(self, platform: str = None) -> List[Account]:
        """Get accounts, optionally filtered by platform."""
        if platform:
            return [a for a in self.accounts if a.platform == platform]
        return self.accounts

    def get_platforms(self) -> Dict:
        """Get available platforms."""
        return self.platforms

    def get_status(self) -> Dict:
        """Get account manager status."""
        return {
            "total_accounts": len(self.accounts),
            "by_platform": {
                platform: len([a for a in self.accounts if a.platform == platform])
                for platform in set(a.platform for a in self.accounts)
            },
            "available_platforms": len(self.platforms),
            "platforms": list(self.platforms.keys()),
        }

    def create_account_plan(self, platform: str) -> Dict:
        """Get account creation plan for a platform."""
        if platform not in self.platforms:
            return {"error": f"Unknown platform: {platform}"}

        info = self.platforms[platform]

        return {
            "platform": platform,
            "name": info["name"],
            "url": info["url"],
            "required": {
                "email": info.get("email_required", True),
                "phone": info.get("phone_required", False),
            },
            "automation": info.get("automation", "manual"),
            "steps": self._get_creation_steps(platform, info),
        }

    def _get_creation_steps(self, platform: str, info: Dict) -> List[str]:
        """Get creation steps for a platform."""
        base_steps = [
            f"1. Go to {info['url']}",
            "2. Enter email: andilexmchunu@gmail.com",
            "3. Verify email",
        ]

        if info.get("phone_required"):
            base_steps.append("4. Verify phone number")

        base_steps.extend(
            [
                "5. Set username (Skywalkingzulu + platform)",
                "6. Complete any required setup",
                "7. Enable API access if needed",
                "8. Save credentials",
            ]
        )

        return base_steps


# Singleton
_account_manager = None


def get_account_manager() -> AccountManager:
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager


if __name__ == "__main__":
    print("=== Andile Account Manager ===\n")

    manager = get_account_manager()

    # Add existing accounts
    print("Adding existing accounts...")
    manager.add_account(
        "github",
        "Skywalkingzulu1",
        "andilesizophila@gmail.com",
        capabilities=["repo", "actions", "pages"],
    )
    manager.add_account(
        "impossible_cloud",
        "andilexmchunu",
        "andilexmchunu@gmail.com",
        "416231769007",
        ["storage", "api"],
    )
    manager.add_account(
        "gmail",
        "andilexmchunu",
        "andilexmchunu@gmail.com",
        capabilities=["smtp", "api"],
    )

    print("\n=== Status ===")
    status = manager.get_status()
    print(json.dumps(status, indent=2))

    print("\n=== Available Platforms ===")
    for key, info in manager.get_platforms().items():
        print(f"  - {key}: {info['name']}")

    print("\n=== Creation Plan Example (GitHub) ===")
    plan = manager.create_account_plan("github")
    print(json.dumps(plan, indent=2))
