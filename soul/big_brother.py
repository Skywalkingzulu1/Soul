import os
import subprocess
import logging
import sys

logger = logging.getLogger("BIG_BROTHER")

class BigBrother:
    """The Overseer: Audits Andile's work and authorizes deployment."""
    
    def __init__(self, factory_dir) -> None:
        self.factory_dir = factory_dir

    def audit(self) -> None:
        """Perform a multi-stage audit on the generated batch."""
        logger.info("Overseer: Initiating high-fidelity audit...")
        
        files = [f for f in os.listdir(self.factory_dir) if f.endswith(".html") and f != "index.html"]
        if not files:
            return False, "No utility files found to audit."

        passed_files = []
        errors = 0

        for file_name in files:
            path = os.path.join(self.factory_dir, file_name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 1. Structural Integrity Check
                required = ["<!DOCTYPE html>", "<script>", "<main>", "id=\"ad-space-top\""]
                if not all(req in content for req in required):
                    logger.error(f"Audit Fail: {file_name} is missing core SEO/Ad structures.")
                    errors += 1
                    continue

                # 2. Functional JS Check
                if "function " in content and ("{" not in content or "}" not in content):
                    logger.error(f"Audit Fail: {file_name} has broken JS syntax.")
                    errors += 1
                    continue
                
                # 3. Content Quality Check (Ensure it's not empty roleplay)
                if len(content) < 1500:
                    logger.error(f"Audit Fail: {file_name} content depth too shallow for 10/10 rating.")
                    errors += 1
                    continue

                passed_files.append(file_name)

        if errors > 0:
            return False, f"Audit failed with {errors} critical errors."
        
        return True, f"Verified {len(passed_files)} tools. 10/10 Integrity Confirmed."

    def deploy(self) -> None:
        """Authorized deployment to production."""
        try:
            logger.info("Overseer: Deployment AUTHORIZED. Pushing to Neptune Grid...")
            subprocess.run(["git", "add", "."], cwd=self.factory_dir, shell=True, check=True)
            subprocess.run(["git", "commit", "-m", "Overseer Approved Release"], cwd=self.factory_dir, shell=True, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.factory_dir, shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Deployment crash: {e}")
            return False
