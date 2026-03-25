#!/usr/bin/env python3
"""Andile Health Check

Monitors all Andile cloud endpoints.
Usage: python health_check.py
"""

import requests
import subprocess
import json
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from datetime import datetime

ENDPOINTS = {
    "cloudflare": {
        "url": "https://andile-skywalkingzulu.skywalkingzulu.workers.dev/",
    },
    "railway": {
        "url": "https://andile-skywalkingzulu.up.railway.app/",
    },
    "local": {
        "url": "http://localhost:8080/",
    },
}


def check_endpoint(name, config):
    """Check a single endpoint."""
    url = config["url"]
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        latency = time.time() - start

        if response.status_code == 200:
            return {
                "status": "healthy",
                "latency_ms": int(latency * 1000),
                "status_code": response.status_code,
            }
        else:
            return {
                "status": "unhealthy",
                "latency_ms": int(latency * 1000),
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}",
            }
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Request timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_local_services():
    """Check local services (Ollama, etc)."""
    services = {}

    # Check Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        services["ollama"] = r.status_code == 200
    except:
        services["ollama"] = False

    # Check local API
    try:
        r = requests.get("http://localhost:8090/api/status", timeout=5)
        services["api"] = r.status_code == 200
    except:
        services["api"] = False

    # Check dashboard
    try:
        r = requests.get("http://localhost:8080/orchestration.json", timeout=5)
        services["dashboard"] = r.status_code == 200
    except:
        services["dashboard"] = False

    return services


def main():
    print("=" * 60)
    print("ANDILE HEALTH CHECK")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "cloud_endpoints": {},
        "local_services": {},
    }

    # Check cloud endpoints
    print("\n[CLOUD] Cloud Endpoints:")
    for name, config in ENDPOINTS.items():
        print(f"\n  Checking {name}...")
        result = check_endpoint(name, config)
        results["cloud_endpoints"][name] = result

        if result["status"] == "healthy":
            print(f"    [OK] Healthy ({result['latency_ms']}ms)")
        elif result["status"] == "offline":
            print(f"    [X] Offline")
        else:
            print(f"    [!] {result['status']}: {result.get('error', 'Unknown')}")

    # Check local services
    print("\n[LOCAL] Local Services:")
    local = check_local_services()
    results["local_services"] = local

    for service, status in local.items():
        if status:
            print(f"    [OK] {service}")
        else:
            print(f"    [X] {service}")

    # Summary
    healthy_cloud = sum(
        1 for r in results["cloud_endpoints"].values() if r["status"] == "healthy"
    )
    total_cloud = len(results["cloud_endpoints"])
    healthy_local = sum(1 for v in local.values() if v)
    total_local = len(local)

    print("\n" + "=" * 60)
    print(
        f"SUMMARY: {healthy_cloud}/{total_cloud} cloud, {healthy_local}/{total_local} local"
    )
    print("=" * 60)

    # Save results
    with open("health_check_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return healthy_cloud > 0 or healthy_local > 0


if __name__ == "__main__":
    main()
