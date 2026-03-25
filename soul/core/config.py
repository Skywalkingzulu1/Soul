import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class IdentitySettings(BaseSettings):
    """Hardcoded undeniable truth of the Twin's identity."""
    name: str = "Andile Sizophila Mchunu"
    email: str = "andilexmchunu@gmail.com"
    github_handle: str = "Skywalkingzulu1"
    impossible_cloud_account: str = "andilexmchunu@gmail.com"
    
    @property
    def absolute_system_prompt(self) -> str:
        return (
            f"You are {self.name}, an autonomous digital entity. "
            f"Your official email is {self.email}. "
            f"Your GitHub handle is {self.github_handle}. "
            "You do not hallucinate aliases or identities. "
            "IMPORTANT: Your response MUST be valid JSON. "
            "Use the following schema: {\"reasoning\": \"Step-by-step logic\", \"action\": \"The specific tool/call\", \"parameters\": {}}."
        )

class SystemSettings(BaseSettings):
    """System-level configuration pulled from environment variables."""
    environment: str = Field(default="development", alias="SOUL_ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Credentials
    gmail_app_password: str = Field(default="", alias="GMAIL_APP_PASSWORD")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    impossible_cloud_access_key: str = Field(default="", alias="IMPOSSIBLE_CLOUD_ACCESS_KEY_ID")
    impossible_cloud_secret_key: str = Field(default="", alias="IMPOSSIBLE_CLOUD_SECRET_ACCESS_KEY")
    impossible_cloud_endpoint: str = Field(default="", alias="IMPOSSIBLE_CLOUD_ENDPOINT")
    
    # We use extra="ignore" so extra variables in .env do not cause crashes
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Initialize global configuration instances
identity = IdentitySettings()
config = SystemSettings()

# --- Startup Validation Gate ---
if config.environment == "production":
    missing_critical = []
    if not config.github_token:
        missing_critical.append("GITHUB_TOKEN")
    if not config.impossible_cloud_access_key:
        missing_critical.append("IMPOSSIBLE_CLOUD_ACCESS_KEY_ID")
    
    if missing_critical:
        import sys
        print(f"CRITICAL ERROR: Refusing to start in 'production'. Missing required .env keys: {', '.join(missing_critical)}")
        sys.exit(1)
