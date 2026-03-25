import asyncio
import re
import logging
from browser.automator import Browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def track_deployer(contract_address):
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        # Step 1: Get Deployer Address from BscScan
        url = f"https://bscscan.com/address/{contract_address}"
        logger.info(f"Navigating to {url}")
        await browser.goto(url)
        await asyncio.sleep(5)
        
        content = await browser.get_page_content()
        
        # Look for "Creator" or "Deployer" text and extract the address
        # BscScan usually shows "Contract Creator: 0x... at txn 0x..."
        creator_match = re.search(r'(?i)(?:contract creator|deployer).*?(0x[a-fA-F0-9]{40})', content)
        
        if creator_match:
            deployer_address = creator_match.group(1)
            logger.info(f"Deployer Address Found: {deployer_address}")
        else:
            # Fallback regex just looking for other addresses on the page
            addresses = re.findall(r'0x[a-fA-F0-9]{40}', content)
            addresses = [a for a in addresses if a.lower() != contract_address.lower()]
            deployer_address = addresses[0] if addresses else "UNKNOWN"
            logger.warning(f"Could not cleanly extract deployer. Guessing: {deployer_address}")

        if deployer_address == "UNKNOWN":
            return {"error": "Deployer address not found."}

        # Step 2: Analyze Deployer History
        deployer_url = f"https://bscscan.com/address/{deployer_address}"
        logger.info(f"Analyzing deployer history: {deployer_url}")
        await browser.goto(deployer_url)
        await asyncio.sleep(5)
        
        deployer_content = await browser.get_page_content()
        
        # Look for token creation events or other contracts
        # Usually represented by "Create" or "Contract Creation"
        creation_count = deployer_content.lower().count("contract creation")
        creation_count += deployer_content.lower().count("create")
        
        # Step 3: Check TokenSniffer for Deployer
        await browser.goto(f"https://tokensniffer.com/address/{deployer_address}")
        await asyncio.sleep(5)
        sniffer_content = await browser.get_page_content()
        
        pattern_indicators = []
        if "scam" in sniffer_content.lower(): pattern_indicators.append("Flagged for previous scams")
        if "honeypot" in sniffer_content.lower(): pattern_indicators.append("History of honeypot deployments")
        
        logger.info("DEPLOYER TRACKING COMPLETE.")
        return {
            "contract": contract_address,
            "deployer": deployer_address,
            "contract_creations_detected": creation_count,
            "pattern_indicators": pattern_indicators,
            "raw_deployer_data_snippet": deployer_content[:1000]
        }

    finally:
        await browser.close()

if __name__ == "__main__":
    siren_contract = "0x997a58129890bbda032231a52ed1ddc845fc18e1"
    result = asyncio.run(track_deployer(siren_contract))
    import json
    print("\n" + "="*50)
    print("  DEPLOYER PATTERN ANALYSIS")
    print("="*50)
    print(json.dumps(result, indent=2))
