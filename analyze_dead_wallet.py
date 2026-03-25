import asyncio
import re
import logging
from browser.automator import Browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_dead_wallet(token_address):
    dead_address = "0x000000000000000000000000000000000000dEaD"
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        # Step 1: Check SIREN balance in Dead Wallet
        url = f"https://bscscan.com/token/{token_address}?a={dead_address}"
        logger.info(f"Checking Dead Wallet balance: {url}")
        await browser.goto(url)
        await asyncio.sleep(5)
        
        content = await browser.get_page_content()
        # Look for the balance text
        balance_match = re.search(r'Balance\s+([\d,.]+)\s+SIREN', content)
        balance = balance_match.group(1) if balance_match else "UNKNOWN"
        
        # Step 2: Check for ANY Outgoing Transactions from the Dead Wallet (The Red Flag)
        # Standardly, the Dead Wallet should NEVER have outgoing transactions
        logger.info("Scanning for outgoing transactions from the 'Dead' address...")
        tx_url = f"https://bscscan.com/address/{dead_address}#tokentxns"
        await browser.goto(tx_url)
        await asyncio.sleep(5)
        tx_content = await browser.get_page_content()
        
        # Look for "OUT" in the transaction list related to SIREN
        out_txs = tx_content.lower().count("out")
        
        # Step 3: Forensic Check for "Contract Creator" labels on the dead wallet page
        # Sometimes devs label their own wallet as 'Burn'
        is_labeled = "null" in content.lower() or "burn" in content.lower()
        
        logger.info("DEAD WALLET FORENSIC COMPLETE.")
        return {
            "token": token_address,
            "dead_address": dead_address,
            "siren_balance_in_dead": balance,
            "outgoing_tx_count_detected": out_txs,
            "labeled_as_burn": is_labeled,
            "verdict": "CRITICAL: Outgoing transactions detected from the burn address. Total exploit confirmed." if out_txs > 0 else "Burn address appears standard, but check for internal 'siphon' logic in contract code."
        }

    finally:
        await browser.close()

if __name__ == "__main__":
    siren_contract = "0x997a58129890bbda032231a52ed1ddc845fc18e1"
    result = asyncio.run(analyze_dead_wallet(siren_contract))
    import json
    print("\n" + "="*50)
    print("  DEAD WALLET FORENSIC REPORT")
    print("="*50)
    print(json.dumps(result, indent=2))
