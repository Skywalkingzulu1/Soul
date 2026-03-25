import asyncio
import json
import time
from soul.bunny_cloud import BunnyMagicContainers

async def deploy():
    bunny = BunnyMagicContainers()
    
    app_name = "andile-ollama"
    image = "ollama/ollama:latest"
    region = 7
    
    print(f"Deploying {app_name} to region {region}...")
    res = bunny.create_app(app_name, image, region_id=region)
    
    if "error" in res:
        print(f"Deployment Failed: {res['error']}")
        print(res.get("detail"))
        return

    print(f"Deployment Initialized: {res.get('id')}")
    print("Waiting for application to scale up (approx 60s)...")
    
    for i in range(6):
        time.sleep(10)
        apps = bunny.list_apps()
        # Find our app in the list
        my_app = next((a for a in apps.get("items", []) if a["name"] == app_name), None)
        if my_app:
            status = my_app.get("status")
            print(f"[{ (i+1)*10 }s] Status: {status}")
            if status == "running" or status == 2: # Status codes may vary
                print("\n[SUCCESS] Ollama is online on Bunny.net!")
                print(f"Endpoint: {my_app.get('hostName')}")
                break
        else:
            print(f"[{ (i+1)*10 }s] App not found in list yet...")

if __name__ == "__main__":
    asyncio.run(deploy())
