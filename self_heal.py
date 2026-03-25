#!/usr/bin/env python3
"""Andile Self-Healing System

Auto-restarts failed services and propagates to backup clouds.
Usage: python self_heal.py
"""

import subprocess
import os
import sys
import json
from datetime import datetime


def run_cmd(cmd, timeout=120):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def heal_railway():
    """Redeploy to Railway."""
    print("Attempting Railway redeploy...")
    success, stdout, stderr = run_cmd("railway up --detached", timeout=300)
    if success:
        print("✅ Railway redeploy initiated")
        return True
    else:
        print(f"❌ Railway redeploy failed: {stderr}")
        return False


def heal_cloudflare():
    """Redeploy to Cloudflare."""
    print("Attempting Cloudflare redeploy...")
    success, stdout, stderr = run_cmd("wrangler deploy", timeout=120)
    if success:
        print("✅ Cloudflare redeployed")
        return True
    else:
        print(f"❌ Cloudflare redeploy failed: {stderr}")
        return False


def propagate_to_backup():
    """If main services fail, propagate to backup."""
    print("\n🔄 PROPAGATION: Main services failed, deploying to backup...")

    # This would deploy to Oracle Cloud or other backup
    print("⚠️  Backup propagation not yet configured")
    print("   (Requires Oracle Cloud setup)")

    return False


def heal():
    """Main healing logic."""
    print("=" * 60)
    print("ANDILE SELF-HEAL")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "healed": {},
        "propagation_needed": False,
    }

    # Try healing Railway
    print("\n1. Checking Railway...")
    success_r, _, _ = run_cmd(
        "curl -s -o /dev/null -w '%{http_code}' https://andile-skywalkingzulu.up.railway.app/ --max-time 5"
    )
    if str(success_r) != "200":
        print("   Railway unhealthy, healing...")
        results["healed"]["railway"] = heal_railway()
    else:
        print("   ✅ Railway healthy")
        results["healed"]["railway"] = True

    # Try healing Cloudflare
    print("\n2. Checking Cloudflare...")
    success_c, _, _ = run_cmd(
        "curl -s -o /dev/null -w '%{http_code}' https://andile-skywalkingzulu.skywalkingzulu.workers.dev/ --max-time 5 --connect-timeout 5"
    )
    if str(success_c) != "200":
        print("   Cloudflare unhealthy, healing...")
        results["healed"]["cloudflare"] = heal_cloudflare()
    else:
        print("   ✅ Cloudflare healthy")
        results["healed"]["cloudflare"] = True

    # Check if propagation needed
    all_healed = all(results["healed"].values())
    if not all_healed:
        results["propagation_needed"] = True
        propagate_to_backup()

    # Save results
    with open("heal_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Healing complete. Propagation needed: {results['propagation_needed']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    heal()
