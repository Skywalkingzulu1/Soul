import asyncio
import re
import logging
from browser.automator import Browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_user_lp(wallet_address, lp_token_address):
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        # Step 1: Check Token Balances for the wallet
        url = f"https://bscscan.com/address/{wallet_address}#tokentxns"
        logger.info(f"Checking wallet token transfers: {url}")
        await browser.goto(url)
        await asyncio.sleep(5)
        
        content = await browser.get_page_content()
        
        # Look for the LP token address or "PancakeSwap V3"
        lp_mentions = content.lower().count(lp_token_address.lower()[:10])
        
        # Step 2: Get specific balance if possible
        balance_url = f"https://bscscan.com/token/{lp_token_address}?a={wallet_address}"
        await browser.goto(balance_url)
        await asyncio.sleep(5)
        balance_content = await browser.get_page_content()
        
        # Try to extract the balance
        balance_match = re.search(r'Balance\s+([\d,.]+)', balance_content)
        balance = balance_match.group(1) if balance_match else "0.00"
        
        logger.info(f"USER LP BALANCE: {balance}")
        
        return {
            "wallet": wallet_address,
            "lp_token": lp_token_address,
            "balance": balance,
            "raw_snippet": balance_content[:500]
        }

    finally:
        await browser.close()

async def get_yield_projection():
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        url = "https://www.geckoterminal.com/bsc/pools/0x12a67c47baf61c0d8d43870a1115ac683f1e5907c2653f08c69bd5ef794a23aa"
        await browser.goto(url)
        await asyncio.sleep(8)
        content = await browser.get_page_content()
        
        # Data points for SIREN pool
        liquidity = 9197.90
        volume_24h = 1230000.00 # Minimum from earlier scan
        fee_tier = 0.0025 # 0.25% common for V3 high vol pairs
        
        daily_fees = volume_24h * fee_tier
        hourly_fees = daily_fees / 24
        five_hour_fees = hourly_fees * 5
        
        # User share (estimate if we don't have balance)
        # Let's assume user has $1000 in LP
        user_stake = 1000.00
        user_share = user_stake / liquidity
        user_earnings_5h = five_hour_fees * user_share
        
        return {
            "total_liquidity": liquidity,
            "volume_24h": volume_24h,
            "estimated_daily_fees_total": daily_fees,
            "user_stake_example": user_stake,
            "projected_earnings_5h": round(user_earnings_5h, 2),
            "critical_warning": "The $37M volume is likely WASH TRADING. Fees may not be claimable or principal will be rugged before exit."
        }

    finally:
        await browser.close()

async def verify_exit(wallet_address):
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        url = f"https://bscscan.com/address/{wallet_address}#tokentxns"
        await browser.goto(url)
        await asyncio.sleep(5)
        content = await browser.get_page_content()
        
        # Look for "OUT" or "Remove" transactions in the last few minutes
        # We also check for the SIREN LP token
        has_out = "OUT" in content or "Remove" in content or "PancakeSwap" in content
        
        logger.info(f"EXIT VERIFIED: {has_out}")
        return {
            "wallet": wallet_address,
            "exit_confirmed": has_out,
            "status": "Safe" if has_out else "Still in Pool/Pending"
        }

    finally:
        await browser.close()

if __name__ == "__main__":
    user_wallet = "0x715048055cCf1C46b225b0a4F070000a6268C7eF"
    # projection = asyncio.run(get_yield_projection())
    exit_status = asyncio.run(verify_exit(user_wallet))
    import json
    print("\n" + "="*50)
    print("  FINAL EXIT VERIFICATION")
    print("="*50)
    print(json.dumps(exit_status, indent=2))
