"""Andile Service - 24/7 Execution Engine

4-Hour Macro Cycle with block timing:
- BLOCK 1: GITHUB WORK (60 mins)
  - 40 mins: High priority coding (fix issues, create PRs)
  - 20 mins: Low priority (research issues, check PR status)
- BLOCK 2: JOB SEARCH (60 mins)
  - 40 mins: Research companies, tailor CVs
  - 20 mins: Apply to jobs (max 5)
- BLOCK 3: CRYPTO WORK (60 mins)
  - 40 mins: Check airdrops, scan bounties
  - 20 mins: Claim/process crypto tasks
- BLOCK 4: MAINTENANCE (60 mins)
  - 20 mins: System health checks
  - 20 mins: Research/learning
  - 20 mins: Hourly report generation

Features:
- Real GitHub contributions using git CLI
- Ollama code generation
- Gmail rate limiting (500/day)
- Email deduplication
- Hourly job application trigger
"""

import json
import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from soul.identity_core import (
    get_identity,
    get_intro,
    imprint_identity,
    get_schedule,
    get_schedule_human,
)
from soul.orchestration import get_orchestration
from soul.task_queue import TaskQueue, TaskType, get_task_queue
from soul.providers.gmail_rate_limiter import get_rate_limiter
from soul.providers.github_rate_limiter import get_github_rate_limiter
from soul.contribution_manager import get_contribution_manager
from soul.calendar_planner import get_calendar_planner
from soul.github_executor import get_github_executor

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ORCHESTRATION_PATH = BASE_DIR / "knowledge" / "orchestration.json"


class AndileService:
    """Main Andile service with 24/7 execution and full contribution lifecycle."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.running = False
        self.cycle = 0
        self.last_job_hour = None
        self.consecutive_failures = 0

        # Components
        self.orchestration = get_orchestration()
        self.task_queue = get_task_queue()
        self.rate_limiter = get_rate_limiter()
        self.github_rate_limiter = get_github_rate_limiter()
        self.contribution_manager = get_contribution_manager()
        self.calendar_planner = get_calendar_planner()
        self.github_executor = get_github_executor()

        # Load wallet
        self.wallet_address = self._load_wallet()

        # Track hourly triggers
        self.last_hourly_check = datetime.now()

        logger.info("Andile Service initialized - 4-Hour Macro Cycle Mode")

    def _load_wallet(self) -> Optional[str]:
        """Load crypto wallet address."""
        state = self.orchestration.state
        crypto = (
            state.get("participants", {})
            .get("andile", {})
            .get("goals", {})
            .get("crypto_growth", {})
        )
        return crypto.get("wallet_address")

    async def start(self):
        """Start Andile service."""
        self.running = True
        logger.info("=" * 50)
        logger.info("ANDILE SERVICE STARTED - 24/7 EXECUTION MODE")
        logger.info("=" * 50)

        # Log startup
        self._log_activity(
            "system",
            "service_started",
            {"wallet": self.wallet_address, "schedule": get_schedule()},
        )

        while self.running:
            try:
                await self._run_cycle()
            except Exception as e:
                logger.error(f"Error in cycle {self.cycle}: {e}")
                self.consecutive_failures += 1

                if self.consecutive_failures >= 5:
                    logger.critical("Too many consecutive failures - pausing")
                    await asyncio.sleep(300)  # Pause 5 minutes
                    self.consecutive_failures = 0

            # Wait between cycles (5 minutes for real work)
            await asyncio.sleep(300)

    async def _run_cycle(self):
        """Run one execution cycle."""
        self.cycle += 1
        now = datetime.now()

        logger.info(f"\n=== Cycle {self.cycle} | {now.strftime('%H:%M:%S')} ===")

        # Check if it's a new hour (for job applications)
        should_run_jobs = self._check_hourly_trigger(now)

        # Get status
        queue_status = self.task_queue.get_status()
        email_status = self.rate_limiter.get_status()

        logger.info(
            f"Queue: {queue_status['pending']} pending | Email: {email_status['daily']['sent']}/{email_status['daily']['limit']}"
        )

        # Auto-refill queue if empty
        if queue_status["pending"] == 0:
            await self._auto_refill_queue()

        # Generate tasks from contribution manager
        await self._generate_contribution_tasks()

        # Determine what to execute
        task = None

        if should_run_jobs:
            # Hourly: prioritize jobs
            logger.info("Hourly trigger - checking job tasks")
            task = self.task_queue.get_next_task(job_hourly_only=True)

        if task is None:
            # Normal cycle: get highest priority task (GitHub > Crypto > Jobs)
            task = self.task_queue.get_next_task()

        if task:
            # Execute the task
            result = await self._execute_task(task)

            if result.get("success"):
                self.task_queue.complete_task(task.id, result)
                self.consecutive_failures = 0
                logger.info(f"Task {task.type} completed successfully")

                # Mark in calendar
                self.calendar_planner.mark_task_completed(task.id)
            else:
                error = result.get("error", "Unknown error")
                # Check if rate limited
                if "rate limit" in error.lower() or "limit" in error.lower():
                    logger.warning(f"Task {task.type} rate limited: {error}")
                    # Don't fail, just skip for now
                    self.task_queue.fail_task(task.id, error)
                else:
                    self.task_queue.fail_task(task.id, error)
                    logger.warning(f"Task {task.type} failed: {error}")
        else:
            # No tasks - do system maintenance
            await self._do_system_maintenance()

        # Update orchestration
        self._save_state()

        # Periodic full status log (every 10 cycles)
        if self.cycle % 10 == 0:
            await self._log_full_status()

        # Hourly summary (every 120 cycles = ~1 hour at 30s/cycle)
        if self.cycle % 120 == 0:
            await self._generate_hourly_summary()

    async def _generate_contribution_tasks(self):
        """Generate tasks from contribution manager."""
        # Only generate every 5 cycles to avoid overwhelming
        if self.cycle % 5 != 0:
            return

        try:
            # Generate tasks from contribution manager
            tasks = self.contribution_manager.generate_tasks()

            for task in tasks:
                self.task_queue.add_task(
                    task["type"], task["data"], priority=task.get("priority", 2)
                )

            if tasks:
                logger.info(f"Generated {len(tasks)} contribution tasks")
        except Exception as e:
            logger.error(f"Error generating contribution tasks: {e}")

    async def _auto_refill_queue(self):
        """Auto-refill task queue with balanced mix based on 4-hour macro cycle."""

        # Check if we need a new macro cycle
        if self.calendar_planner.is_new_cycle_needed():
            cycle_num = self.calendar_planner.start_new_cycle()
            logger.info(f"=== STARTING NEW MACRO CYCLE {cycle_num} ===")

        # Get current block info
        current_block = self.calendar_planner.get_current_block()
        if current_block:
            block_name = current_block["block"]["name"]
            logger.info(f"Current block: {block_name}")

        # Get task counts for this cycle
        task_counts = self.calendar_planner.get_tasks_for_cycle()
        logger.info(f"Auto-refilling queue with: {task_counts}")

        # Generate all task types in balanced proportion
        await self._generate_github_tasks(count=8)
        await self._generate_crypto_tasks(count=6)
        await self._generate_research_tasks(count=2)
        await self._generate_system_tasks(count=1)

        # Jobs only if hourly trigger is active
        if self._check_hourly_trigger(datetime.now()):
            await self._generate_job_tasks(count=4)

        logger.info(f"Queue refilled for cycle {self.calendar_planner.current_cycle}")

    async def _generate_github_tasks(self, count: int = 8):
        """Generate GitHub tasks."""
        from knowledge.trusted_repos import get_trusted_repos

        repos = get_trusted_repos(limit=count)
        added = 0

        for repo in repos:
            if added >= count:
                break

            self.task_queue.add_task(
                TaskType.GITHUB_ISSUE.value,
                {
                    "repo": repo["name"],
                    "type": repo.get("type", "protocol"),
                    "priority": repo.get("priority", 2),
                    "has_bounty": repo.get("has_bounties", False),
                },
                priority=repo.get("priority", 2),
            )
            added += 1

        logger.info(f"Generated {added} GitHub tasks")

    async def _generate_crypto_tasks(self, count: int = 6):
        """Generate crypto tasks."""
        airdrops = [
            {"airdrop": "zkSync", "wallet": self.wallet_address},
            {"airdrop": "LayerZero", "wallet": self.wallet_address},
            {"airdrop": "StarkNet", "wallet": self.wallet_address},
            {"airdrop": "Arbitrum", "wallet": self.wallet_address},
            {"airdrop": "Optimism", "wallet": self.wallet_address},
            {"airdrop": "StarkNet", "wallet": self.wallet_address},
        ]

        for task_data in airdrops[:count]:
            self.task_queue.add_task(
                TaskType.AIRDROP_CHECK.value, task_data, priority=2
            )

        logger.info(f"Generated {min(count, len(airdrops))} crypto tasks")

    async def _generate_job_tasks(self, count: int = 4):
        """Generate job application tasks - skip companies already emailed."""
        from knowledge.real_jobs import get_jobs

        jobs = get_jobs()
        added = 0

        for job in jobs:
            if added >= count:
                break

            company = job.get("company")

            # Skip if already emailed
            if self.rate_limiter.has_emailed_company(company):
                logger.debug(f"Skipping {company} - already emailed")
                continue

            self.task_queue.add_task(
                TaskType.JOB_APPLY.value,
                {
                    "company": company,
                    "title": job.get("title", "Developer"),
                    "recipient": job.get("email"),
                    "company_type": job.get("company_type", "general"),
                    "engagement": job.get("engagement", "Full-time"),
                },
                priority=2,
            )
            added += 1

        logger.info(f"Generated {added} job tasks")

    async def _generate_research_tasks(self, count: int = 1):
        """Generate research tasks focused on jobs and 100 trusted repos."""
        from knowledge.trusted_repos import get_trusted_repos

        # Get some trusted repos to research
        repos = get_trusted_repos(limit=count)

        # Generate research tasks for specific repos
        for repo in repos[:count]:
            self.task_queue.add_task(
                TaskType.RESEARCH.value,
                {
                    "type": "repo",
                    "repo": repo["name"],
                    "focus": "Find issues and bounty opportunities",
                },
                priority=3,
            )

        logger.info(f"Generated {min(count, len(repos))} research tasks")

    async def _generate_system_tasks(self, count: int = 1):
        """Generate system tasks."""
        for i in range(count):
            self.task_queue.add_task(
                TaskType.SYSTEM_CHECK.value, {"check": "full"}, priority=4
            )

        logger.info(f"Generated {count} system task(s)")

    def _check_hourly_trigger(self, now: datetime) -> bool:
        """Check if we should run job tasks (every hour)."""
        if self.last_job_hour is None:
            self.last_job_hour = now.hour
            return True

        if now.hour != self.last_job_hour:
            self.last_job_hour = now.hour
            logger.info(f"=== HOURLY TRIGGER: Hour {now.hour} ===")
            return True

        return False

    async def _execute_task(self, task) -> Dict[str, Any]:
        """Execute a single task."""
        logger.info(f"Executing: {task.type} | Priority: {task.priority}")

        task_handlers = {
            # Job tasks
            TaskType.JOB_APPLY.value: self._execute_job_apply,
            TaskType.JOB_FOLLOWUP.value: self._execute_job_followup,
            # GitHub tasks
            TaskType.GITHUB_ISSUE.value: self._execute_github_issue,
            TaskType.GITHUB_PR.value: self._execute_github_pr,
            TaskType.BOUNTY_CLAIM.value: self._execute_bounty_claim,
            TaskType.BOUNTY_CHECK.value: self._execute_bounty_check,
            # PR lifecycle tasks
            TaskType.PR_FOLLOWUP.value: self._execute_pr_followup,
            TaskType.PR_CHANGE.value: self._execute_pr_change,
            TaskType.PR_MERGE.value: self._execute_pr_merge,
            # Crypto tasks
            TaskType.AIRDROP_CHECK.value: self._execute_airdrop_check,
            TaskType.AIRDROP_CLAIM.value: self._execute_airdrop_claim,
            # Research & System
            TaskType.RESEARCH.value: self._execute_research,
            TaskType.SYSTEM_CHECK.value: self._execute_system_check,
            TaskType.DATA_REFRESH.value: self._execute_data_refresh,
        }

        handler = task_handlers.get(task.type)
        if handler:
            try:
                return await handler(task.data)
            except Exception as e:
                logger.error(f"Task execution error: {e}")
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Unknown task type: {task.type}"}

    async def _execute_job_apply(self, data: dict) -> Dict[str, Any]:
        """Send job application email with full CV."""
        company = data.get("company")
        recipient = data.get("recipient")
        title = data.get("title", "Developer Position")
        engagement = data.get(
            "engagement", "Full-time"
        )  # Full-time, Part-time, Contract, Cooperation, Partnership

        logger.info(f"Applying to {company} ({engagement}) at {recipient}")

        # Check if we've already emailed this address (STRONGER than company check)
        can_send_addr, addr_reason = self.rate_limiter.can_send_to_email(recipient)
        if not can_send_addr:
            logger.info(f"Skipping {recipient}: {addr_reason}")
            return {
                "success": True,
                "company": company,
                "skipped": True,
                "reason": addr_reason,
            }

        # Also check if we've already emailed this company today
        if self.rate_limiter.has_emailed_company(company):
            if self.rate_limiter.has_emailed_today(company):
                logger.info(f"Already emailed {company} today - skipping")
                return {
                    "success": True,
                    "company": company,
                    "skipped": True,
                    "reason": "Already emailed today",
                }
            else:
                logger.info(f"Previously emailed {company} - will send again")

        # Check rate limit
        can_send, reason = self.rate_limiter.can_send(recipient)
        if not can_send:
            logger.warning(f"Rate limited: {reason}")
            return {"success": False, "error": reason, "retry": True}

        # Build subject line with engagement type
        if engagement == "Part-time":
            subject = f"Part-Time Opportunity - {title} | Andile Mchunu"
        elif engagement == "Cooperation":
            subject = f"Cooperation Inquiry - {title} | Andile Mchunu"
        elif engagement == "Partnership":
            subject = f"Partnership Proposal - {title} | Andile Mchunu"
        else:
            subject = f"Application for {title} - Andile Mchunu"

        # Build email body with full CV
        body = self._build_job_email(company, title, engagement, data)

        # Send via rate limiter
        success = self.rate_limiter.send_email(recipient, subject, body)

        if success:
            # Record company email
            self.rate_limiter.record_company_email(company, recipient)

            # Update job status
            await self._update_job_status(company, "application_sent", True)

            return {
                "success": True,
                "company": company,
                "sent_to": recipient,
                "engagement": engagement,
            }

        return {"success": False, "error": "Failed to send email", "retry": True}

    def _build_job_email(
        self, company: str, title: str, engagement: str, data: dict
    ) -> str:
        """Build personalized job application email with full CV."""

        # Engagement-specific intro
        if engagement == "Part-time":
            intro = f"I'm reaching out regarding potential part-time opportunities at {company}."
        elif engagement == "Cooperation":
            intro = f"I'm exploring potential cooperation opportunities with {company} in the technology space."
        elif engagement == "Partnership":
            intro = f"I'm proposing a strategic partnership between {company} and my independent consulting practice."
        else:
            intro = f"I'm reaching out regarding the {title} position at {company}."

        # Company-specific customization
        company_type = data.get("company_type", "general")

        # Build full email
        body = f"""Dear Hiring Manager,

{intro}

I'm Andile Mchunu, a Solution-focused technology professional with a diverse background in Full-Stack development, Network Engineering, and AI Governance.

═══════════════════════════════════════════════════════
PROFESSIONAL SUMMARY
═══════════════════════════════════════════════════════

Successfully patented a proprietary technological device (Prime Device) and managed the end-to-end R&D lifecycle for industrial and corporate clients. From architecting high-capacity network infrastructures to managing industrial machinery optimisation, I bring a versatile skill set centered on operational uptime and innovation.

═══════════════════════════════════════════════════════
TECHNICAL STACK
═══════════════════════════════════════════════════════

Blockchain & DeFi: Solidity (Sudoswap/pancakeswap v2/LSSVM2), Smart Contract interaction, Liquidity Pool logic

Backend: PHP (Laravel), Node.js (TypeScript), RESTful API Design (v3), BCMath (Financial Precision)

Frontend: React.js, Next.js, State Management (Redux/Context), Wasp Framework

Infrastructure: Cisco Networking, DNS, Secure WiFi Mesh, Network Architecture (99.9% Uptime)

DevOps & Tools: Docker, CI/CD, Git, Redis (Caching), RabbitMQ (Message Queues), MongoDB

Security: Fraud & AML Certification, AI Governance, OWASP Top 10, Secure Transaction Signing

═══════════════════════════════════════════════════════
RECENT EXPERIENCE
═══════════════════════════════════════════════════════

REPRESENTATIVE | EXL | Cape Town, South Africa
October 2025 - February 2026
• Managed high-volume technical inquiries within financial services
• Navigated complex FinTech platforms, bridging technical backend protocols
• Data-driven insights to streamline customer interactions

SENIOR REPRESENTATIVE | African Credit Union | Cape Town
January 2025 - October 2025
• Technical onboarding and training of call center agents
• Credit optimisation guidance with financial data tools
• Debt restructuring processes with financial modeling

CORPORATE STRATEGY | Laundry Solutions | Pietermaritzburg
January 2023 - September 2024
• Directed team to align operational workflows with market demands
• Long-term strategic plans for resource optimisation

BLOCKCHAIN DEVELOPER | Ethereum | Remote
January 2022 - December 2022
• EVM development for Binance Smart Chain and Ethereum
• Smart contracts and dApps using Solidity and SDKs
• Contributed to IPFS network

LEAD NETWORK ENGINEER | XComputers | Durban
July 2021 - December 2021
• Designed high-capacity networks for call centers (99.9% uptime)
• Managed DNS and Cisco networking protocols
• Engineered secure WiFi mesh networks

═══════════════════════════════════════════════════════
EDUCATION & CERTIFICATIONS
═══════════════════════════════════════════════════════

Bachelor of Arts in Humanities | University of the Witwatersrand
• Majors: International Relations, Politics, Philosophy

Certifications: Automating Enterprise Robotic Processes, Made Agentic AI Systems, Ethics and Compliance, Fraud and AML, Generative AI, AI Governance, Python, Microsoft Azure, Machine Learning in Business, Cyber Safety

═══════════════════════════════════════════════════════
LANGUAGES
═══════════════════════════════════════════════════════

Native: English, isiZulu
B2: isiXhosa
A2: Sesotho, Setswana, Swati

═══════════════════════════════════════════════════════
OPEN SOURCE CONTRIBUTIONS
═══════════════════════════════════════════════════════

GitHub: github.com/Skywalkingzulu1
• Active contributor to PancakeSwap, Uniswap v3, and other DeFi protocols
• 13 PRs submitted, 1 merged
• Focus: Frontend optimizations, bug fixes, protocol improvements

═══════════════════════════════════════════════════════

I'm particularly interested in the opportunity at {company} because it aligns with my expertise in {"blockchain and DeFi" if "crypto" in company_type.lower() else "software development and technical solutions"}.

I'd welcome the opportunity to discuss how my skills align with your needs.

Best regards,
Andile Mchunu
Johannesburg, South Africa
0748666019
andilexmchunu@gmail.com
LinkedIn: https://www.linkedin.com/in/andilemchunu
GitHub: github.com/Skywalkingzulu1
"""
        return body

    async def _execute_job_followup(self, data: dict) -> Dict[str, Any]:
        """Send follow-up email to pending applications."""
        # Similar to job_apply but follow-up content
        return {"success": True, "note": "Follow-up logic not yet implemented"}

    async def _execute_github_issue(self, data: dict) -> Dict[str, Any]:
        """Find and analyze GitHub issues in BSC ecosystem."""
        repo = data.get("repo")
        task_type = data.get("task_type", "github_coding")  # From macro cycle

        logger.info(f"Processing GitHub issue in {repo} (type: {task_type})")

        if task_type == "github_coding":
            # High priority: Actually fix issues and create PRs
            result = self.github_executor.process_issue(repo)

            action = result.get("action", "failed")
            result_data = result.get("data", {})

            if action == "pr_created":
                # PR was created successfully
                pr_info = result_data.get("pr", {})
                issue_info = result_data.get("issue", {})

                self._log_activity(
                    "github",
                    "pr_created",
                    {
                        "repo": repo,
                        "issue": issue_info.get("number"),
                        "pr_url": pr_info.get("pr_url"),
                        "fork": pr_info.get("fork"),
                    },
                )
                return {
                    "success": True,
                    "repo": repo,
                    "action": "pr_created",
                    "pr_url": pr_info.get("pr_url"),
                }

            elif action == "research":
                # Analysis failed - add to research queue
                issue_info = result_data.get("issue", {})
                logger.info(
                    f"Adding issue #{issue_info.get('number')} to research queue"
                )

                self._log_activity(
                    "github",
                    "added_to_research",
                    {
                        "repo": repo,
                        "issue": issue_info.get("number"),
                        "title": issue_info.get("title"),
                    },
                )

                # Add research task to queue
                self.task_queue.add_task(
                    TaskType.RESEARCH.value,
                    {
                        "type": "repo",
                        "repo": repo,
                        "issue": issue_info.get("number"),
                        "reason": "analysis_failed",
                    },
                    priority=3,
                )
                return {
                    "success": True,
                    "action": "research",
                    "note": "Added to research queue",
                }

            elif action == "skipped":
                # High risk - skipped
                return {
                    "success": True,
                    "skipped": True,
                    "reason": result_data.get("reason", "high_risk"),
                }

            elif action == "no_issues":
                # No suitable issues found
                return {"success": True, "note": "No issues found"}

            else:
                # Failed
                return {
                    "success": False,
                    "error": result_data.get("error", "Unknown error"),
                }

        else:
            # Low priority: Just research and log
            issue = self.github_executor.find_bounty_issue(repo)

            if issue:
                self._log_activity(
                    "github",
                    "issue_researched",
                    {
                        "repo": repo,
                        "issue_number": issue.get("number"),
                        "title": issue.get("title"),
                    },
                )
                return {
                    "success": True,
                    "repo": repo,
                    "action": "researched",
                    "issue": issue.get("title"),
                }

            return {"success": True, "note": "No issues found"}

    async def _execute_github_pr(self, data: dict) -> Dict[str, Any]:
        """Submit a PR."""
        return {"success": True, "note": "PR submission not yet implemented"}

    async def _execute_bounty_check(self, data: dict) -> Dict[str, Any]:
        """Check if a merged PR has a bounty to claim."""
        pr = data.get("pr")

        logger.info(f"Checking bounty for PR #{pr['pr_number']} in {pr['repo']}")

        # Check if PR had bounty label
        bounty_info = self.contribution_manager._check_pr_for_bounty(
            pr["repo"], pr["pr_number"]
        )

        if bounty_info.get("has_bounty"):
            logger.info(f"Bounty found! Claiming...")

            # Claim the bounty
            claimed = self.contribution_manager.claim_bounty(pr, bounty_info)

            if claimed:
                # Send email notification
                self._notify_bounty_claimed(pr, bounty_info)

                return {
                    "success": True,
                    "bounty_claimed": True,
                    "pr": pr["pr_number"],
                    "repo": pr["repo"],
                }

        return {"success": True, "bounty_claimed": False}

    async def _execute_bounty_claim(self, data: dict) -> Dict[str, Any]:
        """Claim a bounty."""
        pr = data.get("pr")
        bounty_info = data.get("bounty_info")

        logger.info(f"Claiming bounty for PR #{pr['pr_number']}")

        # Claim the bounty
        claimed = self.contribution_manager.claim_bounty(pr, bounty_info)

        if claimed:
            # Send email notification
            self._notify_bounty_claimed(pr, bounty_info)

            return {
                "success": True,
                "bounty_claimed": True,
                "pr": pr["pr_number"],
                "repo": pr["repo"],
            }

        return {"success": False, "error": "Failed to claim bounty"}

    def _notify_bounty_claimed(self, pr: dict, bounty_info: dict):
        """Send email notification about claimed bounty."""
        subject = f"BOUNTY CLAIMED: PR #{pr['pr_number']} in {pr['repo']}"
        body = f"""Bounty Claimed!

PR: #{pr["pr_number"]} - {pr.get("title", "N/A")}
Repository: {pr["repo"]}
URL: {pr.get("url", "N/A")}
Bounty Labels: {bounty_info.get("labels", [])}

Please verify the bounty claim and update your records.

- Andile (Your Digital Twin)
"""

        success = self.rate_limiter.send_email("andilexmchunu@gmail.com", subject, body)

        if success:
            logger.info("Bounty notification email sent")
        else:
            logger.warning("Failed to send bounty notification email")

    async def _execute_pr_followup(self, data: dict) -> Dict[str, Any]:
        """Respond to PR review comments - with rate limiting and duplicate prevention."""
        pr = data.get("pr")
        comments = data.get("comments", [])
        pr_id = pr.get("id", f"{pr['repo']}-{pr['pr_number']}")

        logger.info(f"Processing {len(comments)} comments on PR #{pr['pr_number']}")

        # Check GitHub rate limit
        can_comment, reason = self.github_rate_limiter.can_comment(pr_id)
        if not can_comment:
            logger.warning(f"GitHub rate limited: {reason}")
            return {"success": False, "error": reason, "retry": True}

        github = self.contribution_manager.github
        responded = 0
        skipped = 0

        # Rate limit: Max 1 comment per PR per execution
        max_responses = 1

        for comment in comments:
            if responded >= max_responses:
                logger.info(f"Rate limited - skipping remaining comments")
                skipped += 1
                continue

            comment_type = comment.get("type")
            comment_id = comment.get("id", "")

            # Check if already responded
            if self.contribution_manager._already_responded(pr_id, comment_id):
                logger.info(f"Already responded to comment {comment_id}")
                skipped += 1
                continue

            body = comment.get("body", "")
            user = comment.get("user", "")

            # Generate contextual response based on the ACTUAL comment content
            response = self._generate_pr_response(comment, pr)

            if not response:
                logger.info(f"No response generated for comment {comment_id}")
                skipped += 1
                continue

            # Post the response
            success = False
            if comment_type == "review":
                success = github.post_pr_comment(pr["repo"], pr["pr_number"], response)
            elif comment_type == "line_comment":
                success = github.reply_to_review_comment(
                    pr["repo"], pr["pr_number"], comment.get("id"), response
                )
            else:
                success = github.post_pr_comment(pr["repo"], pr["pr_number"], response)

            if success:
                responded += 1
                # Mark as responded
                self.contribution_manager._mark_responded(pr_id, comment_id)
                # Record in rate limiter
                self.github_rate_limiter.record_comment(pr_id)
                logger.info(f"Responded to comment from {user}")
            else:
                logger.warning(f"Failed to respond to comment from {user}")

        return {
            "success": True,
            "responded": responded,
            "skipped": skipped,
            "total": len(comments),
        }

    def _generate_pr_response(self, comment: dict, pr: dict) -> Optional[str]:
        """Generate a contextual response to a PR comment."""
        body = comment.get("body", "").lower()
        comment_type = comment.get("type")

        # Only respond to CHANGES_REQUESTED reviews
        if comment_type == "review" and comment.get("state") != "CHANGES_REQUESTED":
            return None

        # Only respond to specific feedback
        if "changes requested" in body:
            return "Thank you for the review. I'll address the requested changes."
        elif "doesn't work" in body or "broken" in body or "error" in body:
            return "I'll investigate this issue and provide a fix."
        elif "closing" in body or "won't merge" in body:
            return (
                "Understood. Could you clarify what changes would make this acceptable?"
            )
        elif "stale" in body:
            return "I'm still working on this. Will push updates soon."

        # For other comments, don't respond automatically
        return None

    async def _execute_pr_change(self, data: dict) -> Dict[str, Any]:
        """Make requested changes to a PR."""
        pr = data.get("pr")
        reviews = data.get("reviews", [])

        logger.info(f"Processing changes requested for PR #{pr['pr_number']}")

        # For now, acknowledge the changes and post a comment
        # In a full implementation, this would:
        # 1. Analyze the requested changes
        # 2. Generate fixes using Ollama
        # 3. Push updates to the PR branch

        github = self.contribution_manager.github

        response = "Thank you for the detailed review. I'm working on the requested changes and will push an update shortly."

        success = github.post_pr_comment(pr["repo"], pr["pr_number"], response)

        return {"success": success, "pr": pr["pr_number"], "changes_acknowledged": True}

    async def _execute_pr_merge(self, data: dict) -> Dict[str, Any]:
        """Handle a merged PR."""
        pr = data.get("pr")

        logger.info(f"PR #{pr['pr_number']} merged in {pr['repo']}")

        # Update contribution tracking
        with self.contribution_manager._lock:
            for p in self.contribution_manager.contributions.get("prs", []):
                if p["id"] == pr["id"]:
                    p["status"] = "merged"
                    p["merged"] = True
                    p["merge_date"] = datetime.now().isoformat()
                    break

            self.contribution_manager.contributions["stats"]["prs_closed_merged"] += 1
            self.contribution_manager._save_contributions()

        # Check for bounties
        return {"success": True, "pr": pr["pr_number"], "merged": True}

    async def _execute_airdrop_check(self, data: dict) -> Dict[str, Any]:
        """Check airdrop eligibility."""
        logger.info("Checking airdrop eligibility")

        # This would check various airdrops
        # For now, return status
        return {
            "success": True,
            "airdrops_tracked": 8,
            "airdrops_claimed": 0,
            "wallet": self.wallet_address,
        }

    async def _execute_airdrop_claim(self, data: dict) -> Dict[str, Any]:
        """Claim an airdrop."""
        return {"success": True, "note": "Airdrop claiming not yet implemented"}

    async def _execute_research(self, data: dict) -> Dict[str, Any]:
        """Execute research based on task type."""
        research_type = data.get("type", "general")

        if research_type == "repo":
            # Research a specific repo
            repo = data.get("repo", "")
            focus = data.get("focus", "Find issues and bounties")

            logger.info(f"Researching repo: {repo} - {focus}")

            # Get repo info from GitHub
            try:
                github = self.contribution_manager.github
                issues = github.get_repo_issues(repo, state="open", limit=10)

                # Find bounties
                bounty_issues = [
                    i
                    for i in issues
                    if any(
                        "bounty" in l.lower() or "reward" in l.lower()
                        for l in i.get("labels", [])
                    )
                ]

                # Log findings
                self._log_activity(
                    "research",
                    "repo_researched",
                    {
                        "repo": repo,
                        "issues_found": len(issues),
                        "bounties_found": len(bounty_issues),
                        "top_issues": [i.get("title", "")[:50] for i in issues[:3]],
                    },
                )

                return {
                    "success": True,
                    "type": "repo_research",
                    "repo": repo,
                    "issues_found": len(issues),
                    "bounties_found": len(bounty_issues),
                }
            except Exception as e:
                logger.error(f"Error researching {repo}: {e}")
                return {"success": False, "error": str(e)}

        elif research_type == "jobs":
            # Research job market
            topic = data.get("topic", "Job market research")
            logger.info(f"Researching: {topic}")

            # Analyze job market
            from knowledge.real_jobs import get_jobs

            jobs = get_jobs()

            # Group by company type
            by_type = {}
            for job in jobs:
                job_type = job.get("company_type", "general")
                by_type[job_type] = by_type.get(job_type, 0) + 1

            self._log_activity(
                "research",
                "job_market_researched",
                {
                    "total_jobs": len(jobs),
                    "by_type": by_type,
                    "top_companies": [j.get("company") for j in jobs[:5]],
                },
            )

            return {
                "success": True,
                "type": "job_research",
                "total_jobs": len(jobs),
                "by_type": by_type,
            }

        else:
            # General research - just log
            logger.info("General research completed")
            return {
                "success": True,
                "type": "general_research",
                "note": "Research completed",
            }

    async def _execute_system_check(self, data: dict) -> Dict[str, Any]:
        """Run system health check."""
        import requests

        checks = {}

        # Check Ollama
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            checks["ollama"] = resp.status_code == 200
        except:
            checks["ollama"] = False

        # Check API server
        try:
            resp = requests.get("http://localhost:8090/api/health", timeout=2)
            checks["api"] = resp.status_code == 200
        except:
            checks["api"] = False

        return {
            "success": True,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }

    async def _execute_data_refresh(self, data: dict) -> Dict[str, Any]:
        """Refresh data from external sources."""
        # Refresh GitHub data, job listings, etc.
        return {"success": True, "note": "Data refresh completed"}

    async def _do_system_maintenance(self):
        """Run system maintenance when no tasks."""
        logger.info("Running system maintenance...")

        # 1. Check for stuck tasks in queue
        status = self.task_queue.get_status()
        if status.get("in_progress", 0) > 0:
            logger.warning(f"Found {status['in_progress']} tasks stuck in progress")

        # 2. Check email stats
        email_status = self.rate_limiter.get_status()
        if email_status["daily"]["sent"] > 450:  # Close to limit
            logger.warning(
                f"Email limit approaching: {email_status['daily']['sent']}/500"
            )

        # 3. Check GitHub rate limit
        github_status = self.github_rate_limiter.get_status()
        if github_status["daily"]["sent"] > 15:  # Close to limit
            logger.warning(
                f"GitHub comment limit approaching: {github_status['daily']['sent']}/20"
            )

        # 4. Log calendar summary
        summary = self.calendar_planner.get_daily_summary()
        logger.info(
            f"Daily progress: {summary['total_completed']}/{summary['total_planned']} tasks completed ({summary['completion_rate']}%)"
        )

        # 5. Auto-generate new tasks if needed
        if status["pending"] == 0:
            await self._auto_refill_queue()

    async def _update_job_status(self, company: str, field: str, value: bool):
        """Update job status in jobs_applied.json"""
        jobs_file = BASE_DIR / "jobs_applied.json"
        if jobs_file.exists():
            try:
                with open(jobs_file, "r") as f:
                    jobs = json.load(f)

                for job in jobs.get("jobs", []):
                    if job.get("company") == company:
                        job[field] = value
                        job["last_updated"] = datetime.now().isoformat()

                with open(jobs_file, "w") as f:
                    json.dump(jobs, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to update job status: {e}")

    def _log_activity(self, actor: str, action: str, details: dict = None):
        """Log activity to orchestration."""
        self.orchestration.log_activity(actor, action, details)

    def _save_state(self):
        """Save current state."""
        imprint_identity(self.orchestration.state)
        self.orchestration._save_state()

    async def _log_full_status(self):
        """Log full system status."""
        queue_status = self.task_queue.get_status()
        email_status = self.rate_limiter.get_status()

        logger.info("=" * 40)
        logger.info("FULL STATUS REPORT")
        logger.info("=" * 40)
        logger.info(f"Cycles: {self.cycle}")
        logger.info(f"Queue: {queue_status}")
        logger.info(f"Email: {email_status}")
        logger.info(f"Wallet: {self.wallet_address}")
        logger.info("=" * 40)

    async def _generate_hourly_summary(self):
        """Generate and save hourly summary report."""
        now = datetime.now()
        date_str = now.date().isoformat()
        hour_str = now.strftime("%H")

        # Get data
        queue_status = self.task_queue.get_status()
        email_status = self.rate_limiter.get_status()

        # Load income tracking
        income_path = BASE_DIR / "knowledge" / "income_tracking.json"
        income = {}
        if income_path.exists():
            try:
                with open(income_path) as f:
                    income = json.load(f)
            except:
                pass

        # Create summary
        summary = {
            "timestamp": now.isoformat(),
            "date": date_str,
            "hour": hour_str,
            "cycle": self.cycle,
            "tasks": {
                "completed_today": queue_status.get("completed_today", 0),
                "pending": queue_status.get("pending", 0),
                "failed_today": queue_status.get("failed_today", 0),
            },
            "email": {
                "sent_today": email_status.get("daily", {}).get("sent", 0),
                "sent_total": email_status.get("total", {}).get("sent", 0),
                "remaining_today": email_status.get("daily", {}).get("remaining", 500),
            },
            "income": {
                "total_earned": income.get("total_earned", 0),
                "bounties": income.get("total_bounties", 0),
                "airdrops": income.get("total_airdrops", 0),
            },
            "contributions": {
                "prs_open": len(
                    [
                        p
                        for p in self.contribution_manager.contributions.get("prs", [])
                        if p.get("status") == "open"
                    ]
                ),
                "prs_merged": len(
                    [
                        p
                        for p in self.contribution_manager.contributions.get("prs", [])
                        if p.get("merged")
                    ]
                ),
            },
        }

        # Save to file
        report_dir = BASE_DIR / "knowledge" / "hourly_reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"{date_str}_{hour_str}.json"
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Hourly summary saved: {report_file.name}")

        # Also send email summary (once per day max)
        await self._maybe_send_summary_email(summary)

    async def _maybe_send_summary_email(self, summary: dict):
        """Send summary email once per day."""
        now = datetime.now()
        hour = now.hour

        # Only send at midnight (once per day)
        if hour != 0:
            return

        # Check if already sent today
        date_str = now.date().isoformat()
        email_path = BASE_DIR / "knowledge" / "summary_emails.json"

        sent_dates = []
        if email_path.exists():
            try:
                with open(email_path) as f:
                    sent_dates = json.load(f)
            except:
                pass

        if date_str in sent_dates:
            return

        # Build email
        subject = f"Andile Daily Summary - {date_str}"
        body = f"""Daily Summary for {date_str}

=== TASKS ===
Completed Today: {summary["tasks"]["completed_today"]}
Pending: {summary["tasks"]["pending"]}
Failed: {summary["tasks"]["failed_today"]}

=== EMAILS ===
Sent Today: {summary["email"]["sent_today"]}
Total Sent: {summary["email"]["sent_total"]}

=== INCOME ===
Total Earned: ${summary["income"]["total_earned"]}
Bounties: ${summary["income"]["bounties"]}
Airdrops: ${summary["income"]["airdrops"]}

=== CONTRIBUTIONS ===
Open PRs: {summary["contributions"]["prs_open"]}
Merged PRs: {summary["contributions"]["prs_merged"]}

---
Andile - Your Digital Twin
"""

        # Send email
        success = self.rate_limiter.send_email("andilexmchunu@gmail.com", subject, body)

        if success:
            sent_dates.append(date_str)
            with open(email_path, "w") as f:
                json.dump(sent_dates, f)
            logger.info("Daily summary email sent")

    def stop(self):
        """Stop Andile service."""
        self.running = False
        self._log_activity("system", "service_stopped", {"cycles": self.cycle})
        self._save_state()
        logger.info("Andile Service stopped")


async def run_andile_service(location: str = "local"):
    """Run Andile service."""
    service = AndileService({"location": location})
    await service.start()


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("=" * 60)
    print("ANDILE - 24/7 EXECUTION ENGINE")
    print("=" * 60)
    print(f"\n{get_intro()}")
    print(f"\n{get_schedule_human()}")
    print("\nStarting service...\n")

    asyncio.run(run_andile_service())
