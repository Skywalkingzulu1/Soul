import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class BunnyMagicContainers:
    """Interface for Bunny.net Magic Containers API (2026)."""
    
    BASE_URL = "https://api.bunny.net/mc"
    
    def __init__(self, api_key=None) -> None:
        self.api_key = api_key or "4c28d39b-9090-46e2-993e-deaf895b07f2a29f3ec9-0cfd-41d0-8089-7537f2e5b6aa"
        self.headers = {
            "AccessKey": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def list_apps(self) -> None:
        """List all Magic Containers applications."""
        url = f"{self.BASE_URL}/apps"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def list_regions(self) -> None:
        """List available Magic Containers regions."""
        url = f"{self.BASE_URL}/regions"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def create_app(self, name, image, region_id=7) -> None:
        """Create a new Magic Container application."""
        url = f"{self.BASE_URL}/apps"
        payload = {
            "Name": name,
            "RegionSettings": [
                {
                    "RegionId": region_id,
                    "IsEnabled": True,
                    "IsBaseRegion": True
                }
            ],
            "Containers": [
                {
                    "Image": image,
                    "Name": "main"
                }
            ]
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code in (200, 201):
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def get_app(self, app_id) -> None:
        """Get details of a specific Magic Container application."""
        url = f"{self.BASE_URL}/apps/{app_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def update_app(self, app_id, image, name=None, region_id=7) -> None:
        """Update a Magic Container application (image, etc)."""
        url = f"{self.BASE_URL}/apps/{app_id}"
        current = self.get_app(app_id)
        if "error" in current:
            return current
            
        # Parse image
        tag = "latest"
        if ":" in image:
            image, tag = image.split(":")
        
        namespace = ""
        image_name = image
        if "/" in image:
            namespace, image_name = image.split("/")

        payload = {
            "name": name or current.get("name"),
            "runtimeType": current.get("runtimeType", "shared"),
            "autoScaling": current.get("autoScaling", {"min": 1, "max": 1}),
            "regionSettings": {
                "allowedRegionIds": [region_id if isinstance(region_id, str) else "DE"], # DE is Germany
                "requiredRegionIds": [region_id if isinstance(region_id, str) else "DE"],
                "maxAllowedRegions": 1,
                "provisioningType": "static"
            },
            "containerTemplates": [
                {
                    "id": "app",
                    "name": "app",
                    "image": f"{image}:{tag}",
                    "imageName": image_name,
                    "imageNamespace": namespace,
                    "imageTag": tag,
                    "imagePullPolicy": "always",
                    "imageRegistryId": "1155",
                    "endpoints": [
                        {
                            "displayName": "Ollama API",
                            "type": "cdn",
                            "cdn": {
                                "isSslEnabled": False,
                                "portMappings": [
                                    {
                                        "containerPort": 11434
                                    }
                                ]
                            },
                            "portMappings": [
                                {
                                    "containerPort": 11434
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code in (200, 204):
                return {"status": "updated"}
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

    def delete_app(self, app_id) -> None:
        """Delete a Magic Container application."""
        url = f"{self.BASE_URL}/apps/{app_id}"
        try:
            response = requests.delete(url, headers=self.headers, timeout=15)
            if response.status_code == 204:
                return {"status": "deleted"}
            return {"error": f"API returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    bunny = BunnyMagicContainers()
    print("Listing Regions:")
    regions = bunny.list_regions()
    print(json.dumps(regions, indent=2))
    
    # print("\nCreating Test App (Ollama)...")
    # res = bunny.create_app("andile-ollama", "ollama/ollama:latest")
    # print(json.dumps(res, indent=2))
