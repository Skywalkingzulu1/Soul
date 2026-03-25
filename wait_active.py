import time
import json
from soul.bunny_cloud import BunnyMagicContainers

def wait():
    b = BunnyMagicContainers()
    app_id = "zaAv5Pc7uFBQr8T"
    for i in range(20):
        app = b.get_app(app_id)
        status = app.get("status")
        endpoint = app.get("displayEndpoint", {}).get("address")
        print(f"[{i}] Status: {status} | Endpoint: {endpoint}")
        if status == "active":
            print("SUCCESS: App is active.")
            return True
        time.sleep(15)
    return False

if __name__ == "__main__":
    wait()
