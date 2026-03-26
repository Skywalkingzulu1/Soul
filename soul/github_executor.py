"""GitHub Executor - Real GitHub Contributions (Fork-First Approach)

This module handles actual GitHub work:
1. Find issues with bounties
2. Fork the repository (not clone original)
3. Analyze issues with Ollama
4. Generate code fixes and write to files
5. Create PRs from fork to original
6. Monitor PR status
"""

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

from soul.core.logger import setup_logger
from soul.providers.github_client import get_github_client

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OLLAMA_URL = "http://localhost:11434"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class GitHubExecutor:
    """Handles real GitHub contributions using fork-first approach with git CLI."""

    def __init__(self):
        self.github = get_github_client()
        self.work_dir = BASE_DIR / "github_work"
        self.work_dir.mkdir(exist_ok=True)

    def find_bounty_issue(self, repo: str) -> Optional[dict]:
        """Find an issue to work on in a repo."""
        try:
            issues = self.github.get_repo_issues(repo, state="open", limit=30)

            # First pass: Look for bounty issues
            for issue in issues:
                labels = [l.lower() for l in issue.get("labels", [])]
                has_bounty = any(
                    "bounty" in l or "reward" in l or "💰" in l for l in labels
                )
                if has_bounty:
                    return self._issue_to_dict(repo, issue)

            # Second pass: Look for good first issues or help wanted
            for issue in issues:
                labels = [l.lower() for l in issue.get("labels", [])]
                is_good = any(
                    "good first" in l or "help wanted" in l or "beginner" in l
                    for l in labels
                )
                if is_good:
                    return self._issue_to_dict(repo, issue)

            # Third pass: Look for small issues (size/XS or size/S)
            for issue in issues:
                labels = [l.lower() for l in issue.get("labels", [])]
                is_small = any(
                    "size/xs" in l or "size/s" in l or "bug" in l or "fix" in l
                    for l in labels
                )
                if is_small:
                    return self._issue_to_dict(repo, issue)

            # Fourth pass: Just take any issue
            if issues:
                return self._issue_to_dict(repo, issues[0])

            return None
        except Exception as e:
            logger.error(f"Error finding issues in {repo}: {e}")
            return None

    def _issue_to_dict(self, repo: str, issue: dict) -> dict:
        """Convert issue API response to dict."""
        return {
            "repo": repo,
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "url": issue.get("url", ""),
            "body": (issue.get("body") or "")[:1000],
            "labels": [l.lower() for l in issue.get("labels", [])],
        }

    def analyze_issue_with_ollama(self, issue: dict) -> Optional[dict]:
        """Analyze an issue using Ollama."""
        try:
            prompt = f"""Analyze this GitHub issue and provide a concrete fix:

Repository: {issue["repo"]}
Issue #{issue["number"]}: {issue["title"]}

Description:
{issue.get("body", "No description")[:1500]}

Provide your analysis in this format:
1. PROBLEM: What is the issue?
2. SOLUTION: How to fix it?
3. FILES: Which files need to be modified? (list exact paths)
4. CODE: What code changes are needed?
5. RISK: Is this low/medium/high risk?

Be specific and actionable."""

            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": "gpt-oss:120b-cloud",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert developer specializing in Python, JavaScript, Solidity, and DeFi protocols. Analyze GitHub issues and provide actionable, specific fixes with exact file paths and code changes.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "")

                # Parse risk level
                risk = "medium"
                content_lower = content.lower()
                if "risk: low" in content_lower or "low risk" in content_lower:
                    risk = "low"
                elif "risk: high" in content_lower or "high risk" in content_lower:
                    risk = "high"

                # Parse file paths from FILES section
                files_to_modify = self._extract_file_paths(content)

                return {
                    "analysis": content,
                    "suggested_fix": content,
                    "risk_level": risk,
                    "files_to_modify": files_to_modify,
                    "issue_number": issue.get("number"),
                }

            return None
        except Exception as e:
            logger.error(f"Error analyzing issue with Ollama: {e}")
            return None

    def _extract_file_paths(self, content: str) -> list:
        """Extract file paths from analysis content."""
        import re

        # Look for common file patterns
        patterns = [
            r"(?:^|\n)\s*(?:FILES?|Modified files?|Files to modify):?\s*\n((?:\s*[-*]?\s*\S+\.\w+\n?)+)",
            r"(?:^|\n)\s*[-*]\s*((?:src|lib|contracts|test|\.github)/\S+\.\w+)",
            r"(?:^|\n)\s*[-*]\s*(\S+\.(?:py|js|ts|sol|json|yaml|yml|md))",
        ]

        files = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Clean up the match
                for line in match.strip().split("\n"):
                    line = line.strip().lstrip("-* ")
                    if line and "." in line and not line.startswith("#"):
                        files.append(line)

        return list(set(files))[:5]  # Max 5 files

    def generate_code_fix(self, issue: dict, analysis: dict) -> Optional[str]:
        """Generate code fix using Ollama."""
        try:
            prompt = f"""Generate the exact code fix for this GitHub issue:

Issue #{issue["number"]}: {issue["title"]}
Repository: {issue["repo"]}

Analysis:
{analysis.get("analysis", "")[:500]}

Files to modify: {", ".join(analysis.get("files_to_modify", []))}

Generate ONLY the code changes. Use this format for each file:
--- FILE: path/to/file.ext ---
[complete new file content or just the changed section]

Be precise and production-ready."""

            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": "gpt-oss:120b-cloud",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert developer. Generate precise, production-ready code fixes. Output code that can be directly applied to fix the issue.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
                timeout=180,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")

            return None
        except Exception as e:
            logger.error(f"Error generating code fix: {e}")
            return None

    def fork_repo(self, repo: str) -> Optional[str]:
        """Fork a repository. Returns fork full_name."""
        logger.info(f"Forking {repo}...")

        # Create new fork (skip checking if exists - fork is idempotent)
        fork = self.github.fork_repo(repo)
        if fork:
            # Wait for fork to be ready
            logger.info(f"Fork created/exists: {fork}. Waiting for it to be ready...")
            time.sleep(15)  # GitHub needs time to initialize fork
            return fork

        logger.error(f"Failed to fork {repo}")
        return None

    def clone_and_create_pr(
        self, repo: str, issue: dict, fix_code: str, analysis: dict
    ) -> Optional[dict]:
        """Fork repo, clone fork, apply fix, and create PR."""
        try:
            # 1. Fork repo
            fork = self.fork_repo(repo)
            if not fork:
                logger.error(f"Cannot proceed without fork of {repo}")
                return None

            # 2. Get username
            username = self.github.get_username()

            # 3. Prepare directory
            fork_dir = self.work_dir / fork.replace("/", "_")
            if fork_dir.exists():
                shutil.rmtree(fork_dir)

            # 4. Clone fork (not original)
            clone_url = f"https://{GITHUB_TOKEN}@github.com/{fork}.git"
            logger.info(f"Cloning fork: {fork}")
            result = subprocess.run(
                f"git clone {clone_url} {fork_dir}",
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"Failed to clone fork: {result.stderr}")
                return None

            # 5. Add upstream and fetch
            subprocess.run(
                f"git remote add upstream https://github.com/{repo}.git",
                shell=True,
                cwd=fork_dir,
                capture_output=True,
            )
            subprocess.run(
                "git fetch upstream",
                shell=True,
                cwd=fork_dir,
                capture_output=True,
            )

            # 6. Create branch from upstream/main
            branch_name = (
                f"fix/issue-{issue['number']}-{datetime.now().strftime('%Y%m%d')}"
            )
            subprocess.run(
                f"git checkout -b {branch_name} upstream/main",
                shell=True,
                cwd=fork_dir,
                capture_output=True,
            )

            # 7. Configure git
            subprocess.run(
                "git config user.email 'andilexmchunu@gmail.com'",
                shell=True,
                cwd=fork_dir,
            )
            subprocess.run(
                "git config user.name 'Andile Mchunu'",
                shell=True,
                cwd=fork_dir,
            )

            # 8. Write fix to file(s)
            files_written = self.write_fix_to_file(fork_dir, fix_code, analysis)
            if not files_written:
                # If no files written, create a documentation file with the fix
                doc_file = fork_dir / f"fix_suggestion_{issue['number']}.md"
                with open(doc_file, "w") as f:
                    f.write(f"# Fix Suggestion for Issue #{issue['number']}\n\n")
                    f.write(f"## Issue\n{issue['title']}\n\n")
                    f.write(f"## Analysis\n{analysis.get('analysis', 'N/A')}\n\n")
                    f.write(f"## Suggested Fix\n{fix_code}\n")
                files_written = [str(doc_file)]

            # 9. Check if there are changes
            status_result = subprocess.run(
                "git status --porcelain",
                shell=True,
                cwd=fork_dir,
                capture_output=True,
                text=True,
            )
            if not status_result.stdout.strip():
                logger.warning("No changes to commit - fix may not have been applied")
                # Still commit the documentation
                subprocess.run("git add -A", shell=True, cwd=fork_dir)
                commit_msg = f"docs: Suggested fix for issue #{issue['number']}"
                subprocess.run(
                    f'git commit -m "{commit_msg}"',
                    shell=True,
                    cwd=fork_dir,
                )
            else:
                # 10. Add and commit
                subprocess.run("git add -A", shell=True, cwd=fork_dir)
                commit_msg = (
                    f"fix: Address issue #{issue['number']} - {issue['title'][:50]}"
                )
                subprocess.run(
                    f'git commit -m "{commit_msg}"', shell=True, cwd=fork_dir
                )

            # 11. Push to fork
            logger.info(f"Pushing to fork: {fork}")
            push_result = subprocess.run(
                f"git push origin {branch_name}",
                shell=True,
                cwd=fork_dir,
                capture_output=True,
                text=True,
            )
            if push_result.returncode != 0:
                logger.error(f"Failed to push to fork: {push_result.stderr}")
                return None

            # 12. Create PR from fork to original
            pr_title = f"fix: {issue['title'][:70]}"
            pr_body = f"""## Summary

Fix for #{issue["number"]}

## Problem
{issue.get("body", "N/A")[:500]}

## Solution
{analysis.get("analysis", "N/A")[:500]}

## Risk Level
{analysis.get("risk_level", "medium")}

## Files Changed
{chr(10).join("- " + f for f in files_written)}

---
*Auto-generated by Andile (Digital Twin)*"""

            # PR head format for forks: "username:branch"
            head = f"{username}:{branch_name}"
            logger.info(f"Creating PR: {repo} <- {head}")

            pr = self.github.create_pr(
                repo=repo,
                title=pr_title,
                body=pr_body,
                head=head,
                base="main",
            )

            if pr:
                pr_url = pr.get("html_url", "")
                pr_number = pr.get("number", "")
                logger.info(f"Created PR #{pr_number}: {pr_url}")
                return {
                    "pr_url": pr_url,
                    "pr_number": pr_number,
                    "branch": branch_name,
                    "fork": fork,
                }

            logger.error("Failed to create PR via API")
            return None

        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None

    def write_fix_to_file(self, repo_dir: Path, fix_code: str, analysis: dict) -> list:
        """Write the fix code to the appropriate file(s)."""
        files_written = []

        # Parse fix_code for file markers
        import re

        file_pattern = r"---\s*FILE:\s*(\S+)\s*---\s*\n(.*?)(?=---\s*FILE:|$)"
        matches = re.findall(file_pattern, fix_code, re.DOTALL)

        if matches:
            for file_path, content in matches:
                full_path = repo_dir / file_path.strip()
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w") as f:
                    f.write(content.strip())

                files_written.append(file_path)
                logger.info(f"Wrote fix to: {file_path}")
        else:
            # No file markers found, use files_to_modify from analysis
            files_to_modify = analysis.get("files_to_modify", [])

            if files_to_modify:
                file_path = repo_dir / files_to_modify[0]

                if file_path.exists():
                    # Append to existing file
                    with open(file_path, "a") as f:
                        f.write(
                            f"\n\n# Fix by Andile for issue #{analysis.get('issue_number', '?')}\n"
                        )
                        f.write(fix_code)
                    files_written.append(files_to_modify[0])
                    logger.info(f"Appended fix to: {files_to_modify[0]}")
                else:
                    # Create new file
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "w") as f:
                        f.write(fix_code)
                    files_written.append(files_to_modify[0])
                    logger.info(f"Created file: {files_to_modify[0]}")
            else:
                # Default: create a fix file
                fix_file = (
                    repo_dir / f"fix_issue_{analysis.get('issue_number', 'unknown')}.py"
                )
                with open(fix_file, "w") as f:
                    f.write(
                        f"# Auto-generated fix\n# Issue: {analysis.get('issue_number', '?')}\n\n"
                    )
                    f.write(fix_code)
                files_written.append(str(fix_file.name))
                logger.info(f"Created fix file: {fix_file.name}")

        return files_written

    def process_issue(self, repo: str) -> dict:
        """Full workflow: find issue -> analyze -> fix -> create PR.

        Returns:
            dict with keys:
                - success: bool
                - action: "pr_created" | "research" | "skipped"
                - data: relevant data (pr_url, issue, etc.)
        """
        logger.info(f"Processing issues in {repo}")

        # 1. Find issue
        issue = self.find_bounty_issue(repo)
        if not issue:
            logger.info(f"No suitable issues found in {repo}")
            return {"success": False, "action": "no_issues", "data": None}

        logger.info(f"Found issue #{issue['number']}: {issue['title']}")

        # 2. Analyze with Ollama
        analysis = self.analyze_issue_with_ollama(issue)
        if not analysis:
            logger.warning("Failed to analyze issue - adding to research queue")
            return {"success": False, "action": "research", "data": {"issue": issue}}

        risk = analysis.get("risk_level", "medium")
        logger.info(f"Analysis complete. Risk: {risk}")

        # Skip high risk issues
        if risk == "high":
            logger.info("Skipping high risk issue")
            return {
                "success": False,
                "action": "skipped",
                "data": {"reason": "high_risk", "issue": issue},
            }

        # 3. Generate code fix
        fix_code = self.generate_code_fix(issue, analysis)
        if not fix_code:
            logger.warning("Failed to generate fix - adding to research queue")
            return {
                "success": False,
                "action": "research",
                "data": {"issue": issue, "analysis": analysis},
            }

        # 4. Fork and create PR
        pr_result = self.clone_and_create_pr(repo, issue, fix_code, analysis)
        if pr_result:
            return {
                "success": True,
                "action": "pr_created",
                "data": {
                    "issue": issue,
                    "analysis": analysis,
                    "pr": pr_result,
                },
            }

        return {
            "success": False,
            "action": "failed",
            "data": {"issue": issue, "error": "PR creation failed"},
        }


# Singleton instance
_github_executor = None


def get_github_executor() -> GitHubExecutor:
    """Get the global GitHub executor instance."""
    global _github_executor
    if _github_executor is None:
        _github_executor = GitHubExecutor()
    return _github_executor
