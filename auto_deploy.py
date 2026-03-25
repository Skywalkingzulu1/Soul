#!/usr/bin/env python3
"""Andile Cloud Deployment Automation

Deploys Andile to multiple cloud platforms via CLI.
Usage: python auto_deploy.py [railway|cloudflare|all]
"""

import subprocess
import os
import sys
import json
import time
from datetime import datetime

DEPLOY_STATUS = {}


def run_cmd(cmd, cwd=None, timeout=300):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def deploy_railway():
    """Deploy to Railway."""
    print("=" * 50)
    print("DEPLOYING TO RAILWAY")
    print("=" * 50)

    # Check if linked
    success, stdout, stderr = run_cmd("railway whoami")
    if not success:
        print("❌ Not logged in to Railway")
        print("   Run: railway login")
        return False

    print("✅ Railway authenticated")

    # Link project if exists
    project_id = "5ca8fdfe-57df-4639-8190-03aef6c98c23"
    run_cmd(f"railway link --project {project_id}")

    # Deploy
    print("Deploying to Railway...")
    success, stdout, stderr = run_cmd("railway up --detached", timeout=600)

    if success:
        print("✅ Railway deployment initiated")
        print(f"   Check status: https://railway.com/project/{project_id}")
        return True
    else:
        print(f"❌ Railway deployment failed: {stderr}")
        return False


def deploy_cloudflare():
    """Deploy to Cloudflare Workers."""
    print("=" * 50)
    print("DEPLOYING TO CLOUDFLARE")
    print("=" * 50)

    # Check auth
    success, stdout, stderr = run_cmd("wrangler whoami")
    if not success:
        print("❌ Not logged in to Cloudflare")
        print("   Run: wrangler login")
        return False

    print("✅ Cloudflare authenticated")

    # Deploy
    success, stdout, stderr = run_cmd("wrangler deploy", timeout=120)

    if success:
        print("✅ Cloudflare Workers deployed")

        # Check if subdomain needed
        if "workers.dev subdomain" in stderr:
            print("⚠️  NOTE: Need to register workers.dev subdomain")
            print("   Go to: https://dash.cloudflare.com/")
            print("   Then deploy again")
        return True
    else:
        print(f"❌ Cloudflare deployment failed: {stderr}")
        return False


def get_status():
    """Get deployment status of all platforms."""
    status = {"timestamp": datetime.now().isoformat(), "platforms": {}}

    # Railway
    success, stdout, _ = run_cmd("railway whoami")
    status["platforms"]["railway"] = {
        "auth": success,
        "deployed": False,
        "url": "https://andile-skywalkingzulu.railway.app",
    }

    # Cloudflare
    success, stdout, _ = run_cmd("wrangler whoami")
    status["platforms"]["cloudflare"] = {
        "auth": success,
        "deployed": False,
        "note": "Needs workers.dev subdomain",
    }

    return status


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    print(f"Andile Cloud Deployer")
    print(f"Target: {target}")
    print()

    results = {}

    if target in ["railway", "all"]:
        results["railway"] = deploy_railway()

    if target in ["cloudflare", "all"]:
        results["cloudflare"] = deploy_cloudflare()

    # Show status
    print()
    print("=" * 50)
    print("DEPLOYMENT STATUS")
    print("=" * 50)
    status = get_status()
    print(json.dumps(status, indent=2))

    return results


if __name__ == "__main__":
    main()
