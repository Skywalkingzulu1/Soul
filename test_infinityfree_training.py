import asyncio
import os
import sys
import logging

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from soul.identity import PROFILE

async def train_andile_infinityfree():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("  TRAINING ANDILE: INFINITYFREE HOSTING REGISTRATION")
    print("=" * 60)
    
    soul = Soul(name=PROFILE["full_name"])
    
    # Andile's real details for the form
    # Using the GMX email we just learned/confirmed
    values = {
        "email": "andilexmchunu@gmail.com", 
        "password": "SecurePassword2026!",
        "confirm_password": "SecurePassword2026!",
        "agree": "true" # For Terms of Service
    }
    
    print(f"\n[Action] Starting signup flow for InfinityFree...")
    print(f"  Target: {values['email']}")
    
    # Direct registration URL
    signup_url = "https://app.infinityfree.net/register"
    
    try:
        # Call the signup flow directly
        # This will use the new logic in soul/flows.py (domain verification, iframe-aware, etc.)
        result = await soul.signup("InfinityFree", signup_url, values=values, session_name="infinityfree_andile")
        
        print(f"\n[Result] {result}")
        
        if result.get("status") == "success":
            print("\n[SUCCESS] Andile has mastered InfinityFree registration!")
        else:
            print("\n[STUCK] Andile hit a hurdle. Manual intervention or logic tweak needed.")
            
    except Exception as e:
        print(f"\n[ERROR] Training interrupted: {e}")

if __name__ == "__main__":
    asyncio.run(train_andile_infinityfree())
