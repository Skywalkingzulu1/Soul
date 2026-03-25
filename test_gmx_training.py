import asyncio
import os
import sys
import logging

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from soul.identity import PROFILE

async def train_andile_gmx():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("  TRAINING ANDILE: GMX CLOUD REGISTRATION")
    print("=" * 60)
    
    soul = Soul(name=PROFILE["full_name"])
    
    # Andile's real details for the form
    values = {
        "first_name": "Andile",
        "last_name": "Mchunu",
        "gender": "male",
        "day": "15",
        "month": "06",
        "year": "1995",
        "email": "andile.sizophila.mchunu@gmx.com", # Desired
        "password": "SecurePassword2026!",
        "confirm_password": "SecurePassword2026!"
    }
    
    print(f"\n[Action] Starting signup flow for GMX...")
    print(f"  Target: {values['email']}")
    
    # We use a custom URL to skip potential landing pages
    signup_url = "https://signup.gmx.com/"
    
    try:
        # Call the signup flow directly
        # Headless=False is already the default in soul.signup
        result = await soul.signup("GMX", signup_url, values=values, session_name="gmx_andile")
        
        print(f"\n[Result] {result}")
        
        if "successful" in result.lower():
            print("\n[SUCCESS] Andile has learned to register for GMX!")
        else:
            print("\n[STUCK] Andile hit a hurdle. Check screenshots and logs.")
            
    except Exception as e:
        print(f"\n[ERROR] Training interrupted: {e}")

if __name__ == "__main__":
    asyncio.run(train_andile_gmx())
