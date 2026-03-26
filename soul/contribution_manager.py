"""Contribution Manager - Full Contribution Lifecycle

Manages:
1. Issue discovery and tracking
2. PR monitoring and follow-up
3. Review comment handling
4. Bounty claiming
5. BSC ecosystem focus (10 projects max)
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from threading import Lock

from soul.core.logger import setup_logger
from soul.providers.github_client import get_github_client, GitHubClient

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRIBUTIONS_FILE = BASE_DIR / "knowledge" / "contributions.json"
COMMENT_TRACKING_FILE = BASE_DIR / "knowledge" / "comment_tracking.json"


class ContributionManager:
    """Manages the full contribution lifecycle."""

    def __init__(self):
        self._lock = Lock()
        self.github = get_github_client()
        self.contributions = self._load_contributions()
        self.comment_tracking = self._load_comment_tracking()
        self.last_pr_check = None
        self.last_issue_scan = None

    def _load_contributions(self) -> dict:
        """Load contributions from file."""
        if CONTRIBUTIONS_FILE.exists():
            try:
                with open(CONTRIBUTIONS_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "prs": [],
            "target_repos": [],
            "stats": {
                "prs_open": 0,
                "prs_closed_merged": 0,
                "prs_closed_not_merged": 0,
                "bounties_found": 0,
                "bounties_claimed": 0,
                "last_scan": None,
            },
        }

    def _load_comment_tracking(self) -> dict:
        """Load comment tracking from file."""
        if COMMENT_TRACKING_FILE.exists():
            try:
                with open(COMMENT_TRACKING_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "responded_comments": {},
            "pr_check_history": {},
            "stats": {"total_responses": 0, "last_cleanup": None},
        }

    def _save_comment_tracking(self):
        """Save comment tracking to file."""
        COMMENT_TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMENT_TRACKING_FILE, "w") as f:
            json.dump(self.comment_tracking, f, indent=2)

    def _save_contributions(self):
        """Save contributions to file."""
        CONTRIBUTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONTRIBUTIONS_FILE, "w") as f:
            json.dump(self.contributions, f, indent=2)

    # ============================================
    # PR MONITORING (Hourly)
    # ============================================

    def check_pr_reviews(self) -> List[dict]:
        """Check all PRs for new review comments (hourly)."""
        tasks = []
        now = datetime.now()

        # Only check if it's been at least 1 hour
        if self.last_pr_check and (now - self.last_pr_check).seconds < 3600:
            return tasks

        self.last_pr_check = now
        logger.info("Checking PR reviews...")

        with self._lock:
            for pr in self.contributions.get("prs", []):
                if pr["status"] != "open":
                    continue

                repo = pr["repo"]
                pr_number = pr["pr_number"]

                # Get PR details
                details = self.github.get_pr_details(repo, pr_number)
                if not details:
                    continue

                # Check if merged
                if details.get("merged"):
                    pr["status"] = "merged"
                    pr["merged"] = True
                    logger.info(f"PR #{pr_number} merged!")

                    # Check for bounty
                    tasks.append(
                        {"type": "bounty_check", "data": {"pr": pr}, "priority": 1}
                    )
                    continue

                # Check if closed without merge
                if details["state"] == "closed" and not details.get("merged"):
                    pr["status"] = "closed_not_merged"
                    continue

                # Get review comments
                reviews = self.github.get_pr_reviews(repo, pr_number)
                comments = self.github.get_pr_comments(repo, pr_number)
                issue_comments = self.github.get_pr_issue_comments(repo, pr_number)

                # Check for important comments (MUCH more conservative)
                pr_id = pr.get("id", f"{repo}-{pr_number}")
                important_comments = self._filter_important_comments(
                    reviews, comments, issue_comments, pr_id
                )

                # Only create task if there are truly important comments
                # AND we haven't checked this PR in the last hour
                last_check = self.comment_tracking.get("pr_check_history", {}).get(
                    pr_id
                )
                can_check = True

                if last_check:
                    last_check_time = datetime.fromisoformat(last_check)
                    if (now - last_check_time).seconds < 3600:
                        can_check = False

                if important_comments and can_check:
                    logger.info(
                        f"PR #{pr_number} has {len(important_comments)} important comments"
                    )
                    tasks.append(
                        {
                            "type": "pr_followup",
                            "data": {"pr": pr, "comments": important_comments},
                            "priority": 1,
                        }
                    )

                    # Update check history
                    self.comment_tracking.setdefault("pr_check_history", {})[pr_id] = (
                        now.isoformat()
                    )
                    self._save_comment_tracking()

                # Check for changes requested
                changes_requested = [
                    r for r in reviews if r["state"] == "CHANGES_REQUESTED"
                ]
                if changes_requested and can_check:
                    logger.info(f"PR #{pr_number} has changes requested")
                    tasks.append(
                        {
                            "type": "pr_change",
                            "data": {"pr": pr, "reviews": changes_requested},
                            "priority": 1,
                        }
                    )

                # Update last_checked
                pr["last_checked"] = now.isoformat()

            self._save_contributions()

        return tasks

    def _filter_important_comments(
        self,
        reviews: List[dict],
        comments: List[dict],
        issue_comments: List[dict],
        pr_id: str = None,
    ) -> List[dict]:
        """Filter for important comments only - much more conservative."""
        important = []

        # Keywords that indicate ACTUAL importance (not generic words)
        important_keywords = [
            "changes requested",
            "please fix",
            "doesn't work",
            "broken",
            "error in",
            "conflict",
            "reject",
            "won't merge",
            "closing this",
            "stale",
        ]

        # Keywords to NEVER respond to (common review language)
        ignore_keywords = [
            "question",
            "why",
            "how",
            "review",
            "feedback",
            "thanks",
            "looks good",
            "lgtm",
            "approved",
        ]

        # Check reviews - only respond to CHANGES_REQUESTED
        for review in reviews:
            if review["state"] == "CHANGES_REQUESTED":
                comment_id = str(review.get("id", ""))

                # Check if already responded
                if self._already_responded(pr_id, comment_id):
                    continue

                important.append(
                    {
                        "type": "review",
                        "id": comment_id,
                        "user": review["user"],
                        "state": review["state"],
                        "body": review["body"],
                        "date": review.get("submitted_at"),
                    }
                )

        # Check line comments - only respond to specific feedback
        for comment in comments:
            body_lower = comment.get("body", "").lower()

            # Skip if already responded
            if self._already_responded(pr_id, str(comment.get("id", ""))):
                continue

            # Skip if contains ignore keywords
            if any(kw in body_lower for kw in ignore_keywords):
                continue

            # Only include if contains important keywords
            if any(kw in body_lower for kw in important_keywords):
                important.append(
                    {
                        "type": "line_comment",
                        "id": str(comment.get("id", "")),
                        "user": comment["user"],
                        "body": comment["body"],
                        "path": comment.get("path"),
                        "line": comment.get("line"),
                        "date": comment.get("created_at"),
                    }
                )

        # Check issue comments - generally don't respond unless critical
        for comment in issue_comments:
            body_lower = comment.get("body", "").lower()

            # Skip if already responded
            if self._already_responded(pr_id, str(comment.get("id", ""))):
                continue

            # Only respond to critical feedback
            critical_keywords = [
                "closing",
                "reject",
                "won't merge",
                "stale",
                "abandoned",
            ]
            if any(kw in body_lower for kw in critical_keywords):
                important.append(
                    {
                        "type": "issue_comment",
                        "id": str(comment.get("id", "")),
                        "user": comment["user"],
                        "body": comment["body"],
                        "date": comment.get("created_at"),
                    }
                )

        return important

    def _already_responded(self, pr_id: str, comment_id: str) -> bool:
        """Check if we've already responded to this comment."""
        if not pr_id or not comment_id:
            return False

        responded = self.comment_tracking.get("responded_comments", {})
        pr_comments = responded.get(pr_id, [])
        return comment_id in pr_comments

    def _mark_responded(self, pr_id: str, comment_id: str):
        """Mark a comment as responded to."""
        if not pr_id or not comment_id:
            return

        with self._lock:
            responded = self.comment_tracking.setdefault("responded_comments", {})
            pr_comments = responded.setdefault(pr_id, [])

            if comment_id not in pr_comments:
                pr_comments.append(comment_id)
                self.comment_tracking["stats"]["total_responses"] = (
                    self.comment_tracking["stats"].get("total_responses", 0) + 1
                )
                self._save_comment_tracking()

        # Check line comments
        for comment in comments:
            body_lower = comment.get("body", "").lower()
            if any(kw in body_lower for kw in important_keywords):
                important.append(
                    {
                        "type": "line_comment",
                        "user": comment["user"],
                        "body": comment["body"],
                        "path": comment.get("path"),
                        "line": comment.get("line"),
                        "date": comment.get("created_at"),
                    }
                )

        # Check issue comments (general discussion)
        for comment in issue_comments:
            body_lower = comment.get("body", "").lower()
            if any(kw in body_lower for kw in important_keywords):
                important.append(
                    {
                        "type": "issue_comment",
                        "user": comment["user"],
                        "body": comment["body"],
                        "date": comment.get("created_at"),
                    }
                )

        return important

    # ============================================
    # ISSUE SCANNING (BSC Focus)
    # ============================================

    def scan_bsc_issues(self, max_projects: int = 10) -> List[dict]:
        """Scan BSC ecosystem for issues (10 projects max)."""
        tasks = []
        now = datetime.now()

        # Only scan if it's been at least 2 hours
        if self.last_issue_scan and (now - self.last_issue_scan).seconds < 7200:
            return tasks

        self.last_issue_scan = now
        logger.info("Scanning BSC ecosystem for issues...")

        # Use trusted repos list
        from knowledge.trusted_repos import get_trusted_repos

        trusted_repos = get_trusted_repos(limit=max_projects)
        bsc_repos = [r["name"] for r in trusted_repos]

        for repo in bsc_repos:
            try:
                # Get open issues
                issues = self.github.get_repo_issues(repo, state="open", limit=10)

                # Filter for bounty/interesting issues
                for issue in issues[:3]:  # Max 3 per repo
                    # Check if already tracked
                    if not self._is_issue_tracked(repo, issue.get("number")):
                        # Check if issue has bounty labels
                        labels = [l.lower() for l in issue.get("labels", [])]
                        has_bounty = any("bounty" in l or "reward" in l for l in labels)

                        tasks.append(
                            {
                                "type": "github_issue",
                                "data": {
                                    "repo": repo,
                                    "issue_number": issue.get("number"),
                                    "title": issue.get("title", ""),
                                    "url": issue.get("url", ""),
                                    "has_bounty": has_bounty,
                                },
                                "priority": 1 if has_bounty else 2,
                            }
                        )

                time.sleep(0.5)  # Respect rate limits

            except Exception as e:
                logger.error(f"Error scanning {repo}: {e}")

        return tasks

    def _is_issue_tracked(self, repo: str, issue_number: int) -> bool:
        """Check if an issue is already being tracked."""
        for pr in self.contributions.get("prs", []):
            if pr["repo"] == repo and pr.get("issue_number") == issue_number:
                return True
        return False

    # ============================================
    # BOUNTY MANAGEMENT
    # ============================================

    def check_merged_prs_for_bounties(self) -> List[dict]:
        """Check if merged PRs have bounties to claim."""
        tasks = []

        with self._lock:
            for pr in self.contributions.get("prs", []):
                if pr["status"] == "merged" and not pr.get("bounty_claimed"):
                    repo = pr["repo"]
                    pr_number = pr["pr_number"]

                    # Check if associated issue had bounty
                    bounty_info = self._check_pr_for_bounty(repo, pr_number)

                    if bounty_info.get("has_bounty"):
                        logger.info(f"PR #{pr_number} has bounty: {bounty_info}")
                        tasks.append(
                            {
                                "type": "bounty_claim",
                                "data": {"pr": pr, "bounty_info": bounty_info},
                                "priority": 1,
                            }
                        )

        return tasks

    def _check_pr_for_bounty(self, repo: str, pr_number: int) -> dict:
        """Check if a PR is associated with a bounty issue."""
        # Get PR details to find linked issue
        details = self.github.get_pr_details(repo, pr_number)
        if not details:
            return {"has_bounty": False}

        # Check PR body for issue references
        body = details.get("body", "")
        import re

        issue_refs = re.findall(r"#(\d+)", body)

        for issue_num in issue_refs:
            bounty = self.github.check_bounty_label(repo, int(issue_num))
            if bounty and bounty.get("has_bounty"):
                return {
                    "has_bounty": True,
                    "issue_number": issue_num,
                    "labels": bounty.get("labels", []),
                }

        return {"has_bounty": False}

    def claim_bounty(self, pr: dict, bounty_info: dict) -> bool:
        """Claim a bounty for completed work."""
        logger.info(f"Claiming bounty for PR {pr['pr_number']} in {pr['repo']}")

        # Mark as claimed
        with self._lock:
            for p in self.contributions.get("prs", []):
                if p["id"] == pr["id"]:
                    p["bounty_claimed"] = True
                    p["bounty_claimed_at"] = datetime.now().isoformat()
                    break

            self.contributions.setdefault("stats", {}).setdefault("bounties_claimed", 0)
            self.contributions["stats"]["bounties_claimed"] += 1
            self._save_contributions()

        return True

    # ============================================
    # TASK GENERATION
    # ============================================

    def generate_tasks(self) -> List[dict]:
        """Generate tasks based on current state."""
        tasks = []

        # 1. Check PR reviews (hourly)
        pr_tasks = self.check_pr_reviews()
        tasks.extend(pr_tasks)

        # 2. Check for bounties to claim
        bounty_tasks = self.check_merged_prs_for_bounties()
        tasks.extend(bounty_tasks)

        # 3. Scan for new issues (every 2 hours, BSC focus)
        issue_tasks = self.scan_bsc_issues(max_projects=10)
        tasks.extend(issue_tasks)

        return tasks

    # ============================================
    # STATS & STATUS
    # ============================================

    def get_status(self) -> dict:
        """Get contribution status."""
        with self._lock:
            prs = self.contributions.get("prs", [])
            open_prs = [p for p in prs if p.get("status") == "open"]
            merged_prs = [
                p for p in prs if p.get("status") == "merged" or p.get("merged")
            ]
            closed_prs = [p for p in prs if p.get("status") == "closed_not_merged"]

            stats = self.contributions.get("stats", {})

            return {
                "prs_open": len(open_prs),
                "prs_merged": len(merged_prs),
                "prs_closed": len(closed_prs),
                "target_repos": len(self.contributions.get("target_repos", [])),
                "bounties_found": stats.get("bounties_found", 0),
                "bounties_claimed": stats.get("bounties_claimed", 0),
                "last_pr_check": self.last_pr_check.isoformat()
                if self.last_pr_check
                else None,
                "last_issue_scan": self.last_issue_scan.isoformat()
                if self.last_issue_scan
                else None,
                "open_prs": [
                    {
                        "repo": p["repo"],
                        "number": p["pr_number"],
                        "title": p.get("title", "")[:50],
                        "priority": p.get("priority", 3),
                    }
                    for p in open_prs[:10]
                ],
            }


# Singleton instance
_contribution_manager = None


def get_contribution_manager() -> ContributionManager:
    """Get global contribution manager instance."""
    global _contribution_manager
    if _contribution_manager is None:
        _contribution_manager = ContributionManager()
    return _contribution_manager
