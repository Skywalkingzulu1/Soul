"""Extended GitHub Client - Full API Access for Contribution Lifecycle"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from soul.core.config import config
from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class GitHubClient:
    """Extended GitHub API client for full contribution lifecycle."""

    def __init__(self):
        self.token = config.github_token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None

    def _check_rate_limit(self):
        """Check and respect rate limits."""
        if self.rate_limit_remaining < 100:
            if self.rate_limit_reset:
                wait_time = self.rate_limit_reset - time.time()
                if wait_time > 0:
                    logger.warning(f"Rate limit low, waiting {wait_time:.0f}s")
                    time.sleep(min(wait_time, 60))

    def _request(self, method: str, url: str, **kwargs) -> Optional[dict]:
        """Make API request with rate limiting."""
        self._check_rate_limit()

        try:
            resp = requests.request(method, url, headers=self.headers, **kwargs)

            # Update rate limit info
            self.rate_limit_remaining = int(
                resp.headers.get("X-RateLimit-Remaining", 5000)
            )
            reset_time = resp.headers.get("X-RateLimit-Reset")
            if reset_time:
                self.rate_limit_reset = int(reset_time)

            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 201:  # Created
                return resp.json()
            elif resp.status_code == 202:  # Accepted (async operation like fork)
                return resp.json()
            elif resp.status_code == 204:  # No content
                return {"success": True}
            elif resp.status_code == 403:
                logger.error("GitHub API rate limit exceeded")
                return None
            elif resp.status_code == 404:
                # For fork check, 404 means fork doesn't exist yet
                return None
            else:
                logger.error(f"GitHub API error {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"GitHub request failed: {e}")
            return None

    # ============================================
    # USER INFO
    # ============================================

    def get_user_info(self) -> Optional[dict]:
        """Get authenticated user info."""
        user = self._request("GET", f"{self.base_url}/user")
        if user:
            return {
                "login": user["login"],
                "name": user.get("name"),
                "email": user.get("email"),
                "public_repos": user["public_repos"],
                "followers": user["followers"],
                "following": user["following"],
            }
        return None

    # ============================================
    # PULL REQUESTS
    # ============================================

    def get_user_prs(self, state: str = "all", limit: int = 50) -> List[dict]:
        """Get PRs authored by authenticated user."""
        query = f"is:pr+author:{self._get_username()}+state:{state}"
        url = f"{self.base_url}/search/issues?q={query}&per_page={limit}"

        data = self._request("GET", url)
        if not data:
            return []

        prs = []
        for item in data.get("items", []):
            repo = item.get("repository_url", "").split("/")[-2:]
            repo_name = "/".join(repo) if len(repo) == 2 else "unknown"

            prs.append(
                {
                    "number": item["number"],
                    "title": item["title"],
                    "repo": repo_name,
                    "state": item["state"],
                    "html_url": item["html_url"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "labels": [l["name"] for l in item.get("labels", [])],
                }
            )

        return prs

    def get_pr_details(self, repo: str, pr_number: int) -> Optional[dict]:
        """Get detailed PR information."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        pr = self._request("GET", url)

        if pr:
            return {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "merged": pr.get("merged", False),
                "mergeable": pr.get("mergeable"),
                "mergeable_state": pr.get("mergeable_state"),
                "user": pr["user"]["login"],
                "html_url": pr["html_url"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "base_branch": pr["base"]["ref"],
                "head_branch": pr["head"]["ref"],
                "body": pr.get("body", ""),
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "changed_files": pr.get("changed_files", 0),
            }
        return None

    def get_pr_reviews(self, repo: str, pr_number: int) -> List[dict]:
        """Get reviews on a PR."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/reviews"
        reviews = self._request("GET", url)

        if reviews:
            return [
                {
                    "id": r["id"],
                    "user": r["user"]["login"],
                    "state": r["state"],
                    "body": r.get("body", ""),
                    "submitted_at": r.get("submitted_at"),
                }
                for r in reviews
            ]
        return []

    def get_pr_comments(self, repo: str, pr_number: int) -> List[dict]:
        """Get review comments on a PR (line-specific)."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/comments"
        comments = self._request("GET", url)

        if comments:
            return [
                {
                    "id": c["id"],
                    "user": c["user"]["login"],
                    "body": c["body"],
                    "path": c.get("path"),
                    "line": c.get("line"),
                    "created_at": c["created_at"],
                    "updated_at": c["updated_at"],
                }
                for c in comments
            ]
        return []

    def get_pr_issue_comments(self, repo: str, pr_number: int) -> List[dict]:
        """Get issue comments on a PR (general discussion)."""
        url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
        comments = self._request("GET", url)

        if comments:
            return [
                {
                    "id": c["id"],
                    "user": c["user"]["login"],
                    "body": c["body"],
                    "created_at": c["created_at"],
                    "updated_at": c["updated_at"],
                }
                for c in comments
            ]
        return []

    def post_pr_comment(self, repo: str, pr_number: int, body: str) -> bool:
        """Post a comment on a PR."""
        url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
        data = {"body": body}
        result = self._request("POST", url, json=data)
        return result is not None

    def reply_to_review_comment(
        self, repo: str, pr_number: int, comment_id: int, body: str
    ) -> bool:
        """Reply to a specific review comment."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/comments/{comment_id}/replies"
        data = {"body": body}
        result = self._request("POST", url, json=data)
        return result is not None

    def update_pr(
        self, repo: str, pr_number: int, title: str = None, body: str = None
    ) -> bool:
        """Update PR title or description."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        result = self._request("PATCH", url, json=data)
        return result is not None

    # ============================================
    # ISSUES
    # ============================================

    def get_repo_issues(
        self, repo: str, labels: List[str] = None, state: str = "open", limit: int = 30
    ) -> List[dict]:
        """Get issues from a repo with optional label filter."""
        label_str = ",".join(labels) if labels else ""
        url = f"{self.base_url}/repos/{repo}/issues?state={state}&per_page={limit}"
        if label_str:
            url += f"&labels={label_str}"

        issues = self._request("GET", url)

        if issues:
            # Filter out PRs (issues endpoint also returns PRs)
            return [
                {
                    "number": i["number"],
                    "title": i["title"],
                    "url": i["html_url"],
                    "labels": [l["name"] for l in i.get("labels", [])],
                    "created_at": i["created_at"],
                    "updated_at": i["updated_at"],
                    "comments": i.get("comments", 0),
                    "body": i.get("body", "")[:500],
                }
                for i in issues
                if "pull_request" not in i
            ]
        return []

    def get_bounty_issues(self, repo: str) -> List[dict]:
        """Get issues that likely have bounties."""
        bounty_labels = ["bounty", "bounty:", "reward", "bug bounty", "💰", "💸"]
        all_issues = []

        for label in bounty_labels:
            issues = self.get_repo_issues(repo, labels=[label])
            all_issues.extend(issues)

        # Deduplicate
        seen = set()
        unique = []
        for issue in all_issues:
            if issue["number"] not in seen:
                seen.add(issue["number"])
                unique.append(issue)

        return unique

    def get_good_first_issues(self, repo: str) -> List[dict]:
        """Get beginner-friendly issues."""
        labels = ["good first issue", "help wanted", "beginner friendly", "easy"]
        return self.get_repo_issues(repo, labels=labels)

    # ============================================
    # BOUNTIES
    # ============================================

    def check_bounty_label(self, repo: str, issue_number: int) -> Optional[dict]:
        """Check if an issue has bounty labels."""
        url = f"{self.base_url}/repos/{repo}/issues/{issue_number}"
        issue = self._request("GET", url)

        if issue:
            labels = [l["name"].lower() for l in issue.get("labels", [])]
            bounty_labels = [
                l
                for l in labels
                if "bounty" in l or "reward" in l or "💰" in l or "💸" in l
            ]

            if bounty_labels:
                return {
                    "has_bounty": True,
                    "labels": bounty_labels,
                    "title": issue["title"],
                }

        return {"has_bounty": False}

    # ============================================
    # BSC ECOSYSTEM
    # ============================================

    def search_bsc_issues(
        self, keywords: List[str] = None, has_bounty: bool = False
    ) -> List[dict]:
        """Search for BSC ecosystem issues."""
        if not keywords:
            keywords = ["bsc", "binance", "pancakeswap", "venus", "alpaca"]

        all_issues = []

        for keyword in keywords:
            query = f"{keyword}+is:issue+is:open"
            if has_bounty:
                query += "+label:bounty"

            url = f"{self.base_url}/search/issues?q={query}&per_page=10"
            data = self._request("GET", url)

            if data and "items" in data:
                for item in data["items"]:
                    repo = item.get("repository_url", "").split("/")[-2:]
                    repo_name = "/".join(repo) if len(repo) == 2 else "unknown"

                    all_issues.append(
                        {
                            "number": item["number"],
                            "title": item["title"],
                            "repo": repo_name,
                            "url": item["html_url"],
                            "labels": [l["name"] for l in item.get("labels", [])],
                            "created_at": item["created_at"],
                            "comments": item.get("comments", 0),
                        }
                    )

        # Deduplicate
        seen = set()
        unique = []
        for issue in all_issues:
            key = f"{issue['repo']}:{issue['number']}"
            if key not in seen:
                seen.add(key)
                unique.append(issue)

        return unique

    # ============================================
    # FORK AND PR METHODS
    # ============================================

    def fork_repo(self, repo: str) -> Optional[str]:
        """Fork a repository. Returns fork full_name or None."""
        url = f"{self.base_url}/repos/{repo}/forks"
        result = self._request("POST", url)
        if result:
            fork_name = result.get("full_name")
            if fork_name:
                logger.info(f"Forked {repo} -> {fork_name}")
                return fork_name
        logger.error(f"Failed to fork {repo}")
        return None

    def create_pr(
        self, repo: str, title: str, body: str, head: str, base: str = "main"
    ) -> Optional[dict]:
        """Create a pull request.

        Args:
            repo: Original repo (e.g., "pancakeswap/pancake-frontend")
            title: PR title
            body: PR description
            head: Branch spec (e.g., "Skywalkingzulu1:fix/issue-123" for forks)
            base: Target branch (default "main")
        """
        url = f"{self.base_url}/repos/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        result = self._request("POST", url, json=data)
        if result:
            logger.info(f"Created PR: {result.get('html_url')}")
            return result
        logger.error(f"Failed to create PR for {repo}")
        return None

    def check_fork_exists(self, repo: str) -> Optional[str]:
        """Check if we already have a fork of this repo."""
        username = self._get_username()
        owner, repo_name = repo.split("/")
        fork_name = f"{username}/{repo_name}"

        url = f"{self.base_url}/repos/{fork_name}"
        data = self._request("GET", url)
        if data and data.get("fork"):
            return fork_name
        return None

    def get_username(self) -> str:
        """Get authenticated username (public)."""
        return self._get_username()

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_username(self) -> str:
        """Get authenticated username."""
        user = self.get_user_info()
        return user["login"] if user else "unknown"

    def get_rate_limit(self) -> dict:
        """Get current rate limit status."""
        url = f"{self.base_url}/rate_limit"
        data = self._request("GET", url)
        if data:
            return {
                "core": data["resources"]["core"],
                "search": data["resources"]["search"],
            }
        return {}


# Singleton instance
_github_client = None


def get_github_client() -> GitHubClient:
    """Get global GitHub client instance."""
    global _github_client
    if _github_client is None:
        _github_client = GitHubClient()
    return _github_client
