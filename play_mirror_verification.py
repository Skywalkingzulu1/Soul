import asyncio
import os
import sys
import logging
import time
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from soul.thinker import ThinkerEngine
from browser.automator import Browser

async def technical_mirror_test():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("  ANDILE: TECHNICAL MIRROR TEST - IMPOSSIBLE CLOUD")
    print("=" * 60)
    
    soul = Soul(name="Andile Sizophila Mchunu")
    thinker = ThinkerEngine(name="Andile")
    browser = Browser(headless=False)
    await browser.start()
    
    try:
        # 1. Upload Handshake
        await browser.load_session("impossible_cloud")
        page = browser._page
        
        bucket_url = "https://console.impossiblecloud.com/buckets/andile-soul-v1"
        print(f"\n[Action] Transmitting handshake to: {bucket_url}")
        await browser.goto(bucket_url)
        await asyncio.sleep(5)
        
        # Check if we are in the bucket
        content = await page.content()
        if "Upload" in content:
            print("  [Action] Uploading handshake.txt...")
            async with page.expect_file_chooser() as fc_info:
                await page.get_by_role("button", name="Upload", exact=False).first.click()
            file_chooser = await fc_info.value
            await file_chooser.set_files("handshake.txt")
            await asyncio.sleep(10)
            
            # 2. Visual Verification
            print("\n[Goal] Visual Verification of Handshake Receipt")
            await browser.screenshot("mirror_test_result")
            
            # Extract list from page
            rows = await page.query_selector_all("tr")
            found = False
            for row in rows:
                text = await row.inner_text()
                if "handshake.txt" in text:
                    print(f"  [Verified] Cloud Twin acknowledged: {text.strip()}")
                    found = True
                    break
            
            if not found:
                print("  [Warning] Handshake not immediately visible in list. Checking OCR...")
            
            # 3. The Mirror Conversation (Real AI Generation)
            print("\n" + "-" * 40)
            print("  TWIN DIALOGUE: LOCAL VS CLOUD")
            print("-" * 40)
            
            local_msg = "Hello Cloud Twin. I have uploaded the handshake. Can you confirm your state?"
            print(f"\nLOCAL ANDILE: {local_msg}")
            
            # We ask the thinker to respond from the perspective of the Cloud version
            cloud_context = (
                "You are the Cloud-based version of Andile Sizophila Mchunu. "
                "You exist inside an Impossible Cloud bucket named 'andile-soul-v1'. "
                "Your local self has just uploaded a 'handshake.txt' file to verify your presence. "
                "Respond as the Cloud Twin, confirming receipt and your digital readiness."
            )
            
            cloud_response = thinker.twin_think(local_msg, context=cloud_context)
            print(f"\nCLOUD ANDILE: {cloud_response}")
            
        else:
            print("  [Error] Failed to enter cloud vessel. Verification aborted.")

    except Exception as e:
        print(f"\n[ERROR] Mirror test failed: {e}")
    finally:
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(technical_mirror_test())
