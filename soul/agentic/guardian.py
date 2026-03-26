"""The Guardian & Architect Module - Enforcing 'S-Tier' Repo Standards.

Scans, tests, refactors, and iteratively evolves repositories to make them 
commercially viable, functional, and fully deployed.
"""

import os
import subprocess
import logging
import json
import asyncio
from pathlib import Path
from soul.agentic.self_mod import AgenticExecutor

logger = logging.getLogger(__name__)

class RepoGuardian:
    def __init__(self, soul):
        self.soul = soul
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.username = "Skywalkingzulu1"
        self.work_dir = Path("C:/Users/molel/Soul/contributions")
        self.work_dir.mkdir(exist_ok=True)
        self.projects_dir = Path("C:/Users/molel/Soul/projects")
        self.projects_dir.mkdir(exist_ok=True)

    async def perfect_repo(self, repo_name):
        """Iterative Architect Pulse: Understand, Upgrade, and Deploy."""
        logger.info(f"🛡️ Guardian/Architect: Starting mission for {repo_name}")
        
        # 1. Clone/Fetch
        repo_path = self.work_dir / repo_name
        try:
            if not repo_path.exists():
                self._run_git(["clone", f"https://{self.github_token}@github.com/{self.username}/{repo_name}.git", str(repo_path)])
            else:
                self._run_git(["pull"], cwd=repo_path)
        except Exception as e:
            logger.error(f"Git operation failed for {repo_name}: {e}")
            return f"Error: Git operation failed."

        # 2. DISCOVERY: Understand the Goal
        mission = await self._architect_discovery(repo_name, repo_path)
        logger.info(f"🎯 Mission: {mission['summary']}")

        # 3. STRATEGY: Select Iterative Task
        task = await self._architect_strategy(repo_name, repo_path, mission)
        logger.info(f"🛠️ Task: {task['description']}")

        # 4. EXECUTION: Implement Task
        executor = AgenticExecutor(root_path=str(repo_path))
        result = executor.run(mode="task", task_description=task['description']) 
        
        # 5. VERIFICATION: (Bypassed per user request)
        stats = self._analyze_ecosystem(repo_path)
        # We still run it for logging but ignore the 'passed' flag for pushing
        verification = self._verify_integrity(repo_path, stats)
        
        # 6. DEPLOYMENT (If applicable)
        deployment_status = self._deploy_logic(repo_path, stats)

        # 7. FINALIZE: Commit & Push
        has_changes = result.changes_made > 0
        deployable = deployment_status != "Local Execution Only"
        
        # SKIP GUARDRAIL: Push if there are ANY changes, regardless of verification
        if has_changes or deployable:
            status_prefix = "✅" if verification["passed"] else "⚠️"
            commit_msg = f"Architect Upgrade: {task['description']} | Deploy: {deployment_status}"
            logger.info(f"{status_prefix} Guardrail Skipped: Pushing {repo_name} with message: {commit_msg}")
            try:
                self._push_changes(repo_path, commit_msg)
                return commit_msg
            except Exception as e:
                logger.error(f"❌ Failed to push changes for {repo_name}: {e}")
                return f"Error: Push failed for {repo_name}"
        else:
            logger.info(f"ℹ️ Mission status for {repo_name}: No changes detected to push.")
            return f"Repo {repo_name} checked. No changes."

    async def _architect_discovery(self, repo_name, path):
        """Read files to understand what this repo is and what its goal is."""
        discovery_file = self.projects_dir / f"{repo_name}_discovery.json"
        
        # Read key files
        readme = ""
        if (path / "README.md").exists():
            readme = (path / "README.md").read_text(errors="ignore")
        
        structure = []
        for p in path.glob("*"):
            if p.is_file() and not p.name.startswith("."):
                structure.append(p.name)
            elif p.is_dir() and not p.name.startswith("."):
                structure.append(f"{p.name}/")
        
        # Use Thinker directly - if search is blocked, it will use local context
        prompt = (
            f"Analyze this repository '{repo_name}'.\n"
            f"Files: {structure}\n"
            f"README excerpt: {readme[:500]}\n\n"
            "What is the primary purpose of this repo? Summarize in 1 concise sentence. "
            "Do not use JSON or special formatting. If unsure, infer from file names."
        )
        summary = self.soul.thinker.direct(prompt)
        
        discovery = {"repo": repo_name, "summary": summary, "last_scan": str(Path().cwd())}
        with open(discovery_file, "w") as f:
            json.dump(discovery, f)
        
        return discovery

    async def _architect_strategy(self, repo_name, path, discovery):
        """Determine the next best move for this repo's evolution."""
        prompt = (
            f"Repo: {repo_name}\nGoal: {discovery['summary']}\n\n"
            "Suggest ONE specific technical implementation task to make this repo 'commercially viable' or fix a core bug. "
            "Examples: 'Add a responsive CSS layout', 'Implement an API endpoint for X', 'Create a Dockerfile', 'Add a comprehensive README'. "
            "IMPORTANT: DO NOT suggest 'searching', 'analyzing', or 'researching'. You MUST suggest a CODE change. "
            "Respond with ONLY the task description. No JSON, no preamble."
        )
        task_desc = self.soul.thinker.direct(prompt)
        return {"description": task_desc}

    def _deploy_logic(self, path, stats):
        """Attempt autonomous deployment based on detected stack."""
        if (path / "wrangler.toml").exists():
            return "Cloudflare Workers"
        if (path / "index.html").exists() and not (path / "package.json").exists():
            return "GitHub Pages (Static)"
        if (path / "package.json").exists():
            return "NPM Ecosystem (Build Check)"
        return "Local Execution Only"

    def _analyze_ecosystem(self, path):
        if (path / "foundry.toml").exists(): return {"ecosystem": "foundry", "test_cmd": ["forge", "test"]}
        if (path / "hardhat.config.ts").exists(): return {"ecosystem": "hardhat", "test_cmd": ["npx", "hardhat", "test"]}
        if (path / "requirements.txt").exists(): return {"ecosystem": "python", "test_cmd": ["pytest"]}
        if (path / "package.json").exists(): return {"ecosystem": "node", "test_cmd": ["npm", "test"]}
        return {"ecosystem": "unknown", "test_cmd": None}

    def _verify_integrity(self, path, stats):
        results = {"passed": True}
        if stats["test_cmd"]:
            try:
                res = subprocess.run(stats["test_cmd"], cwd=path, capture_output=True, text=True, timeout=60)
                if res.returncode != 0:
                    results["passed"] = False
            except:
                results["passed"] = False
        return results

    def _run_git(self, args, cwd=None):
        subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=True)

    def _push_changes(self, path, message):
        try:
            self._run_git(["add", "."], cwd=path)
            # Check if there are any staged changes
            status = subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True).stdout.strip()
            if not status:
                logger.info(f"ℹ️ No changes to commit for {path.name}")
                return

            self._run_git(["commit", "-m", message], cwd=path)
            self._run_git(["push", "origin", "main"], cwd=path)
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
