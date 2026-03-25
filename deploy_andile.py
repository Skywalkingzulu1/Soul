#!/usr/bin/env python3
"""Andile Deployment Script

Deploys Andile to various cloud providers.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

CLOUD_PROVIDERS = {
    "cloudflare": {
        "cmd": ["wrangler", "deploy"],
        "check": "wrangler --version",
        "requires": ["wrangler"],
        "file": "cloudflare_worker.js",
    },
    "railway": {
        "cmd": ["railway", "up"],
        "check": "railway --version",
        "requires": ["railway"],
        "file": "railway.json",
    },
    "fly": {
        "cmd": ["fly", "deploy"],
        "check": "fly --version",
        "requires": ["fly"],
        "file": "fly.toml",
    },
    "render": {
        "cmd": ["render", "deploy"],
        "check": "render --version",
        "requires": ["render"],
        "file": "render.yaml",
    },
    "vercel": {
        "cmd": ["vercel", "--prod"],
        "check": "vercel --version",
        "requires": ["vercel"],
        "file": "vercel.json",
    },
}


def check_tool(name: str) -> bool:
    """Check if a tool is installed."""
    try:
        result = subprocess.run(
            name.split()[0] + " --version", shell=True, capture_output=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False


def get_available_providers() -> list:
    """Get list of available providers based on installed tools."""
    available = []
    for name, config in CLOUD_PROVIDERS.items():
        if check_tool(config["check"].split()[0]):
            available.append(name)
    return available


def deploy_to_provider(provider: str) -> dict:
    """Deploy to a specific provider."""
    if provider not in CLOUD_PROVIDERS:
        return {"status": "error", "message": f"Unknown provider: {provider}"}

    config = CLOUD_PROVIDERS[provider]

    # Check if required file exists
    if not os.path.exists(config["file"]):
        return {"status": "error", "message": f"File not found: {config['file']}"}

    # Run deployment command
    try:
        result = subprocess.run(
            config["cmd"], capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            return {"status": "success", "provider": provider, "output": result.stdout}
        else:
            return {"status": "error", "provider": provider, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "error", "provider": provider, "error": "Timeout"}
    except Exception as e:
        return {"status": "error", "provider": provider, "error": str(e)}


def deploy_any() -> dict:
    """Try to deploy to any available provider."""
    available = get_available_providers()

    if not available:
        return {
            "status": "error",
            "message": "No deployment tools found. Install wrangler, railway, fly, or vercel.",
            "available_providers": list(CLOUD_PROVIDERS.keys()),
            "how_to_install": {
                "cloudflare": "npm install -g wrangler",
                "railway": "npm install -g @railway/cli",
                "fly": "curl -L https://fly.io/install.sh | sh",
                "vercel": "npm install -g vercel",
            },
        }

    # Try each available provider
    for provider in available:
        result = deploy_to_provider(provider)
        if result["status"] == "success":
            return result

    return {
        "status": "error",
        "message": "Could not deploy to any provider",
        "available": available,
    }


if __name__ == "__main__":
    print("=== Andile Deployment ===\n")

    # Check available providers
    available = get_available_providers()
    print(f"Available providers: {available or 'None'}")
    print(f"All supported: {list(CLOUD_PROVIDERS.keys())}\n")

    # If argument provided, deploy to that provider
    if len(sys.argv) > 1:
        provider = sys.argv[1]
        print(f"Deploying to {provider}...")
        result = deploy_to_provider(provider)
        print(json.dumps(result, indent=2))
    else:
        # Try to deploy to any available
        print("Trying to deploy to any available provider...")
        result = deploy_any()
        print(json.dumps(result, indent=2))
