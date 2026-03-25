"""Andile 14-Day Account Creation Plan

Day-by-day schedule for Andile to create accounts and establish 24/7 operation.
"""

DAY_1_ACCOUNTS = [
    {
        "platform": "cloudflare",
        "priority": 1,
        "reason": "Workers for API, KV for state",
    },
    {"platform": "vercel", "priority": 2, "reason": "Serverless functions"},
]

DAY_2_3_ACCOUNTS = [
    {"platform": "railway", "priority": 1, "reason": "Host full Andile service"},
    {"platform": "render", "priority": 2, "reason": "Backup hosting"},
]

DAY_4_5_ACCOUNTS = [
    {"platform": "docker", "priority": 1, "reason": "Container registry"},
    {"platform": "gitlab", "priority": 2, "reason": "Backup repo hosting"},
]

DAY_6_7_ACCOUNTS = [
    {"platform": "fly_io", "priority": 1, "reason": "Global deployment"},
    {"platform": "replit", "priority": 2, "reason": "Quick prototyping"},
]

DAY_8_10_ACCOUNTS = [
    {"platform": "oracle", "priority": 1, "reason": "2 free VMs - 24/7 potential"},
    {"platform": "netlify", "priority": 2, "reason": "Static hosting + functions"},
]

DAY_11_14_ACCOUNTS = [
    {
        "platform": "crypto_exchanges",
        "priority": 1,
        "reason": "CEX accounts for trading",
    },
    {"platform": "defi", "priority": 1, "reason": "DeFi protocol accounts"},
]


def get_14_day_plan():
    """Return the 14-day account creation plan."""
    plan = []

    # Day 1-2
    for item in DAY_1_ACCOUNTS:
        plan.append({"day": 1, **item})
    for item in DAY_2_3_ACCOUNTS:
        plan.append({"day": 2, **item})

    # Day 3-4
    for item in DAY_2_3_ACCOUNTS:
        plan.append({"day": 3, **item})

    # Day 4-5
    for item in DAY_4_5_ACCOUNTS:
        plan.append({"day": 4, **item})
    for item in DAY_4_5_ACCOUNTS:
        plan.append({"day": 5, **item})

    # Day 6-7
    for item in DAY_6_7_ACCOUNTS:
        plan.append({"day": 6, **item})
    for item in DAY_6_7_ACCOUNTS:
        plan.append({"day": 7, **item})

    # Day 8-10
    for item in DAY_8_10_ACCOUNTS:
        plan.append({"day": 8, **item})
    for item in DAY_8_10_ACCOUNTS:
        plan.append({"day": 9, **item})
    for item in DAY_8_10_ACCOUNTS:
        plan.append({"day": 10, **item})

    # Day 11-14
    for item in DAY_11_14_ACCOUNTS:
        plan.append({"day": 11, **item})
    for item in DAY_11_14_ACCOUNTS:
        plan.append({"day": 12, **item})
    for item in DAY_11_14_ACCOUNTS:
        plan.append({"day": 13, **item})
    for item in DAY_11_14_ACCOUNTS:
        plan.append({"day": 14, **item})

    return plan


def get_current_day_accounts(day: int):
    """Get accounts to create for a specific day."""
    plan = get_14_day_plan()
    return [p for p in plan if p["day"] == day]


if __name__ == "__main__":
    import json

    print("=== Andile 14-Day Account Creation Plan ===\n")

    plan = get_14_day_plan()

    for day in range(1, 15):
        accounts = get_current_day_accounts(day)
        print(f"Day {day}:")
        for acc in accounts:
            print(f"  [{acc['priority']}] {acc['platform']}: {acc['reason']}")
        print()
