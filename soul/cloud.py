import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class ImpossibleCloud:
    """Interface for Impossible Cloud Management API (Partner API)."""
    
    BASE_URL = "https://api.partner.impossiblecloud.com/v1"
    
    def __init__(self, api_key=None) -> None:
        self.api_key = api_key or self._load_key()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    def _load_key(self) -> None:
        cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "cloud_credentials.json")
        if os.path.exists(cred_path):
            with open(cred_path, "r") as f:
                data = json.load(f)
                return data.get("impossible_cloud", {}).get("api_key")
        return None

    def list_contracts(self) -> None:
        """List all contracts associated with the account."""
        url = f"{self.BASE_URL}/contract/list"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def list_storage_accounts(self) -> None:
        """List all storage accounts."""
        url = f"{self.BASE_URL}/storage-account/list"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def list_regions(self) -> None:
        """List available regions (Public endpoint)."""
        url = f"{self.BASE_URL}/integration/regions/list"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_status(self) -> None:
        """Verify API key works."""
        # Try a public endpoint first to confirm BASE_URL
        regions = self.list_regions()
        if "error" in regions:
            return f"Offline: Base URL verification failed ({regions['error']})"
            
        # Confirm authentication
        res = self.list_contracts()
        if isinstance(res, dict) and "error" in res:
            return f"Offline: Authentication failed ({res['error']}). Key format: {len(self.api_key)} chars."
        
        return "Online (Authenticated)"

if __name__ == "__main__":
    cloud = ImpossibleCloud()
    print(f"Status: {cloud.get_status()}")
    if cloud.get_status() == "Online (Authenticated)":
        print("\nContracts:")
        print(json.dumps(cloud.list_contracts(), indent=2))
