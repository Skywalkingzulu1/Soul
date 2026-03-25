import json
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ship():
    base_dir = r"contributions\uniswap_fixes"
    report_path = r"knowledge\github_fixes_report.json"
    
    if not os.path.exists(report_path):
        logger.error("Report not found.")
        return

    with open(report_path, "r") as f:
        fixes = json.load(f)

    # 1. Individual Solidity Files
    for fix in fixes:
        filename = f"Fix_{fix['id']}_{fix['title'].replace(':', '').replace(' ', '_').lower()}.sol"
        filepath = os.path.join(base_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(f"// Title: {fix['title']}\n")
            f.write(f"// Description: {fix['description']}\n")
            f.write("// Author: Skywalkingzulu1 (Andile Sizophila Mchunu)\n")
            f.write("// Goal: Uniswap/ETH Security Fix Collection\n")
            f.write("\n")
            f.write(fix['code'].strip())
            f.write("\n")
        logger.info(f"Created {filename}")

    # 2. README.md
    readme_content = f"""# Uniswap & ETH Security Fixes
A collection of 10 critical security patches for Ethereum and Uniswap (V2/V3) smart contracts.

## Author
**Andile Sizophila Mchunu (Skywalkingzulu1)**
*Specializing in Web3, DeFi, and Smart Contract Security*

## Fixes Included
"""
    for fix in fixes:
        readme_content += f"### {fix['id']}. {fix['title']}\n"
        readme_content += f"{fix['description']}\n\n"

    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(readme_content)
    logger.info("Created README.md")

    # 3. Git Initialization
    try:
        os.chdir(base_dir)
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "chore: ship 10 Uniswap/ETH security fixes"], check=True)
        logger.info("Initialized git and committed changes locally.")
    except Exception as e:
        logger.error(f"Git operations failed: {e}")

if __name__ == "__main__":
    ship()
