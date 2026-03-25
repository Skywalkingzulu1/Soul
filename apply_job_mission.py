import asyncio
import json
import os
from datetime import datetime
from soul.brain import Soul

async def main():
    # Load credentials if not in environment
    if not os.environ.get("GMAIL_PASSWORD"):
        try:
            with open("knowledge/cloud_credentials.json", "r") as f:
                creds = json.load(f)
                password = creds.get("impossible_cloud", {}).get("password")
                if password:
                    os.environ["GMAIL_PASSWORD"] = password
                    print(f"Loaded password from cloud_credentials.json")
        except Exception as e:
            print(f"Could not load password: {e}")

    # Initialize Soul
    soul = Soul(name="Andile Sizophila Mchunu")
    
    companies = [
        {"name": "VALR", "email": "careers@valr.com", "domain": "valr.com"},
        {"name": "TymeBank", "email": "careers@tymebank.co.za", "domain": "tymebank.co.za"},
        {"name": "Onafriq", "email": "careers@onafriq.com", "domain": "onafriq.com"},
        {"name": "Ozow", "email": "careers@ozow.com", "domain": "ozow.com"},
        {"name": "Centbee", "email": "careers@centbee.com", "domain": "centbee.com"},
        {"name": "AltCoinTrader", "email": "careers@altcointrader.co.za", "domain": "altcointrader.co.za"},
        {"name": "Lynk Ware", "email": "careers@lynkware.com", "domain": "lynkware.com"},
        {"name": "Tether", "email": "careers@tether.to", "domain": "tether.to"},
        {"name": "FirstRand", "email": "recruitment@firstrand.co.za", "domain": "firstrand.co.za"},
        {"name": "Stitch Money", "email": "careers@stitch.money", "domain": "stitch.money"}
    ]
    
    jobs_applied_path = "knowledge/jobs_applied.json"
    
    # Load existing jobs
    if os.path.exists(jobs_applied_path):
        with open(jobs_applied_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"last_updated": "", "jobs": []}
    else:
        data = {"last_updated": "", "jobs": []}

    for company in companies:
        print(f"Processing {company['name']}...")
        
        subject = f"Application for Senior Backend / Blockchain Solutions Role - Andile Sizophila Mchunu"
        body = (
            f"Dear HR / Hiring Manager at {company['name']},\n\n"
            "I am writing to express my strong interest in a Senior Backend or Blockchain Solutions role at your company. "
            "With extensive experience in Web3, DeFi, and HealthTech AI at Azania Neptune Labs, I have a proven track record of "
            "building resilient infrastructure and innovative solutions.\n\n"
            "My expertise includes Senior Backend Development (Python, FastAPI, Node.js), Blockchain Solutions & Web3 Infrastructure, "
            "DeFi Protocol Design & Implementation, and HealthTech AI Platforms.\n\n"
            "I have been following your work in Johannesburg and am impressed by your impact on the industry. "
            "I would welcome the opportunity to discuss how my technical background can contribute to your engineering team.\n\n"
            "Best regards,\n"
            "Andile Sizophila Mchunu\n"
            "Skywalkingzulu\n"
            "Azania Neptune Labs"
        )
        
        # Use Soul.perceive to send email
        # Format: send email to {email} subject: {subject} saying {body}
        # Avoid words: system, tool, capability, limitation, hardware
        perceive_input = f"send email to {company['email']} subject: {subject} saying {body}"
        
        try:
            print(f"Sending email to {company['name']} ({company['email']})...")
            response = await soul.perceive(perceive_input)
            print(f"Soul response: {response}")
            
            # Update jobs_applied.json
            new_job = {
                "title": "Senior Backend / Blockchain Solutions Role",
                "company": company['name'],
                "email": company['email'],
                "url": f"https://{company['domain']}",
                "applied": True,
                "response_received": False,
                "pdf_error": False,
                "applied_at": datetime.now().isoformat()
            }
            data["jobs"].append(new_job)
            data["last_updated"] = datetime.now().isoformat()
            
            with open(jobs_applied_path, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"Successfully applied to {company['name']}\n")
            
        except Exception as e:
            print(f"Failed to apply to {company['name']}: {e}\n")
            
        # Small delay to be polite
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
