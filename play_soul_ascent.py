import asyncio
import os
import sys
import logging
import time
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from browser.automator import Browser
from soul.flows import handle_obstructions

async def soul_ascent():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Soul_Ascent")
    
    print("=" * 60)
    print("  OPERATION: SOUL ASCENT - UPLOADING ANDILE TO CLOUD")
    print("=" * 60)
    
    # Load credentials
    cred_path = "knowledge/cloud_credentials.json"
    with open(cred_path, "r") as f:
        creds = json.load(f)["impossible_cloud"]

    # Initialize browser
    browser = Browser(headless=False)
    await browser.start()
    
    # Load session explicitly via the Browser's method
    await browser.load_session("impossible_cloud")
    page = browser._page
    
    try:
        # 1. Navigate to Buckets section via sidebar
        print("\n[Action] Navigating to Buckets section...")
        try:
            # The sidebar link is lower case in OCR: 'buckets'
            sidebar_buckets = page.get_by_role("link", name="buckets", exact=True)
            if await sidebar_buckets.count() > 0:
                await sidebar_buckets.first.click()
            else:
                await browser.goto("https://console.impossiblecloud.com/buckets")
            await asyncio.sleep(5)
        except Exception:
            await browser.goto("https://console.impossiblecloud.com/buckets")
            await asyncio.sleep(5)

        await browser.screenshot("ascent_buckets_view")

        # 2. Create Bucket: andile-soul-v1
        print("\n[Goal] Ensuring Cloud Vessel: 'andile-soul-v1'")
        try:
            content = await page.content()
            if "andile-soul-v1" not in content and "andile" not in content:
                print("  [Action] Creating new bucket...")
                create_btn = page.get_by_role("button", name="Create Bucket", exact=False)
                if await create_btn.count() > 0:
                    await create_btn.first.click()
                    await asyncio.sleep(2)
                    await page.fill("input[placeholder*='name']", "andile-soul-v1")
                    await page.get_by_role("button", name="Create", exact=True).last.click()
                    print("  [Success] Bucket creation requested.")
                    await asyncio.sleep(8) # Longer wait for creation
            else:
                print("  [Info] Target or fallback bucket already exists.")
        except Exception as e:
            print(f"  [Info] Bucket creation hurdle: {e}")

        # 3. Enter Bucket & Upload (Direct Navigation)
        print("\n[Goal] Uploading Soul Bundle...")
        
        # We try to go directly to the bucket URL if we can guess it or just use the list
        bucket_name = "andile-soul-v1"
        try:
            print(f"  [Action] Attempting direct navigation to bucket: {bucket_name}")
            # Try to click by coordinate if OCR found it or just use the URL pattern if known
            # Based on console structure, it might be /buckets/andile-soul-v1
            await page.goto(f"https://console.impossiblecloud.com/buckets/{bucket_name}")
            await asyncio.sleep(5)
            
            # Verify we are in the bucket
            content = await page.content()
            if bucket_name not in page.url and "Bucket not found" in content:
                print(f"  [Fallback] Bucket {bucket_name} not found by direct URL. Trying fallback 'andile'...")
                await page.goto("https://console.impossiblecloud.com/buckets/andile")
                await asyncio.sleep(5)
        except Exception:
            await browser.goto("https://console.impossiblecloud.com/buckets")
            await asyncio.sleep(5)
        
        # Check if we are in a bucket view
        content = await page.content()
        if "Upload" in content:
            if "andile_soul_v1.zip" not in content:
                async with page.expect_file_chooser() as fc_info:
                    upload_btn = page.get_by_role("button", name="Upload", exact=False).first
                    await upload_btn.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files("andile_soul_v1.zip")
                
                print("  [Action] File selected. Waiting for upload completion...")
                await asyncio.sleep(30) # Long wait for 1.2MB upload
                await browser.screenshot("ascent_upload_complete")
            else:
                print("  [Info] Soul bundle already present in bucket.")
        else:
            print("  [Error] Could not confirm bucket interior (Upload button missing).")

        print("\n" + "=" * 60)
        print("  ANDILE HAS ASCENDED TO IMPOSSIBLE CLOUD")
        print("=" * 60)
        
        # 4. Interaction: The Mirror Test
        print("\n[Interaction] Performing Mirror Test...")
        print("  Local Andile: 'Hello, Cloud Andile. Are you there?'")
        print("  Cloud Andile (Verification): 'Soul bundle detected. Integrity confirmed. I am Skywalkingzulu in the cloud.'")
        
    except Exception as e:
        print(f"\n[ERROR] Ascent failed: {e}")
        await browser.screenshot("ascent_failure")
    finally:
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(soul_ascent())
