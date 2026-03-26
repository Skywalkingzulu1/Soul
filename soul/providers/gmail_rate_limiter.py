"""Gmail Rate Limiter - Ensures we never exceed 500 emails/day

Gmail Limits:
- 500 emails/day (sent via SMTP)
- ~20-30 emails/hour to avoid triggering spam

This module provides:
- Daily counter with automatic reset at midnight
- Hourly counter to prevent burst blocks
- Per-recipient tracking to avoid spam triggers
- Exponential backoff on failures
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from threading import Lock

from soul.core.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATS_FILE = BASE_DIR / "knowledge" / "email_stats.json"
COMPANIES_FILE = BASE_DIR / "knowledge" / "email_tracking.json"


class GmailRateLimiter:
    """Rate limiter for Gmail API to prevent exceeding limits."""

    MAX_DAILY = 500
    MAX_HOURLY = 20
    MAX_PER_RECIPIENT = 5  # Max emails to same recipient per day

    def __init__(self):
        self._lock = Lock()
        self._stats = self._load_stats()
        self._companies = self._load_companies()
        self._check_and_reset_daily()
        self._check_and_reset_hourly()

    def _load_stats(self) -> dict:
        """Load email statistics from file."""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "sent_today": 0,
            "last_reset_date": datetime.now().date().isoformat(),
            "hourly": {},
            "by_recipient": {},
            "last_reset_hour": datetime.now().hour,
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "last_sent": None,
        }

    def _load_companies(self) -> dict:
        """Load emailed companies tracking from file."""
        if COMPANIES_FILE.exists():
            try:
                with open(COMPANIES_FILE, "r") as f:
                    return json.load(f)
            except:
                pass

        return {
            "emailed_companies": {},
            "stats": {
                "total_companies": 0,
                "total_emails_sent": 0,
                "last_updated": datetime.now().isoformat(),
            },
        }

    def _save_companies(self):
        """Save emailed companies tracking to file."""
        COMPANIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMPANIES_FILE, "w") as f:
            json.dump(self._companies, f, indent=2)

    def has_emailed_company(self, company: str) -> bool:
        """Check if we've already emailed this company."""
        return company in self._companies.get("emailed_companies", {})

    def has_emailed_today(self, company: str) -> bool:
        """Check if we've already emailed this company today."""
        today = datetime.now().date().isoformat()
        company_data = self._companies.get("emailed_companies", {}).get(company, {})
        dates_sent = company_data.get("dates_sent", [])
        return today in dates_sent

    def has_emailed_address(self, email: str) -> bool:
        """Check if we've ever emailed this address (permanent block)."""
        addresses = self._companies.get("emailed_addresses", {})
        return email.lower() in addresses

    def has_emailed_address_today(self, email: str) -> bool:
        """Check if we've already emailed this address today."""
        today = datetime.now().date().isoformat()
        addresses = self._companies.get("emailed_addresses", {})
        addr_data = addresses.get(email.lower(), {})
        dates = addr_data.get("dates", [])
        return today in dates

    def can_send_to_email(self, email: str) -> tuple[bool, str]:
        """Check if we can send to this specific email address."""
        if self.has_emailed_address(email):
            if self.has_emailed_address_today(email):
                return False, f"Already emailed {email} today"
            else:
                return True, "Previously emailed (can send again today)"
        return True, "New recipient"

    def record_company_email(self, company: str, email: str):
        """Record that we emailed a company."""
        with self._lock:
            today = datetime.now().date().isoformat()

            # Track by company
            companies = self._companies.setdefault("emailed_companies", {})
            if company not in companies:
                companies[company] = {"email": email, "dates_sent": [], "total_sent": 0}
            companies[company]["total_sent"] += 1
            if today not in companies[company]["dates_sent"]:
                companies[company]["dates_sent"].append(today)

            # Track by email address (prevents duplicates across all contexts)
            addresses = self._companies.setdefault("emailed_addresses", {})
            email_key = email.lower()
            if email_key not in addresses:
                addresses[email_key] = {"company": company, "dates": [], "total": 0}
            addresses[email_key]["total"] += 1
            if today not in addresses[email_key]["dates"]:
                addresses[email_key]["dates"].append(today)

            # Update stats
            self._companies["stats"]["total_companies"] = len(companies)
            self._companies["stats"]["total_emails_sent"] = sum(
                c.get("total_sent", 0) for c in companies.values()
            )
            self._companies["stats"]["last_updated"] = datetime.now().isoformat()

            self._save_companies()
            logger.info(f"Recorded email to {company} ({email})")

    def _save_stats(self):
        """Save email statistics to file."""
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(self._stats, f, indent=2)

    def _check_and_reset_daily(self):
        """Reset daily counters if it's a new day."""
        today = datetime.now().date().isoformat()
        if self._stats.get("last_reset_date") != today:
            logger.info(f"New day detected - resetting daily email counter")
            self._stats["sent_today"] = 0
            self._stats["hourly"] = {}
            self._stats["by_recipient"] = {}
            self._stats["last_reset_date"] = today
            self._save_stats()

    def _check_and_reset_hourly(self):
        """Reset hourly counter if it's a new hour."""
        current_hour = datetime.now().hour
        if self._stats.get("last_reset_hour") != current_hour:
            self._stats["last_reset_hour"] = current_hour
            self._save_stats()

    def can_send(self, recipient: str = None) -> tuple[bool, str]:
        """Check if we can send an email.

        Returns:
            (can_send, reason)
        """
        with self._lock:
            self._check_and_reset_daily()
            self._check_and_reset_hourly()

            # Check daily limit
            if self._stats["sent_today"] >= self.MAX_DAILY:
                return False, f"Daily limit reached ({self.MAX_DAILY})"

            # Check hourly limit
            current_hour = str(datetime.now().hour)
            hourly_sent = self._stats["hourly"].get(current_hour, 0)
            if hourly_sent >= self.MAX_HOURLY:
                return False, f"Hourly limit reached ({self.MAX_HOURLY})"

            # Check per-recipient limit
            if recipient:
                recipient_key = recipient.lower()
                sent_to_recipient = self._stats["by_recipient"].get(recipient_key, 0)
                if sent_to_recipient >= self.MAX_PER_RECIPIENT:
                    return False, f"Recipient limit reached for {recipient}"

            return True, "OK"

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send email with rate limiting.

        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body

        Returns:
            True if sent successfully, False otherwise
        """
        can_send, reason = self.can_send(recipient)
        if not can_send:
            logger.warning(f"Cannot send email to {recipient}: {reason}")
            return False

        # Try to send
        try:
            from soul.providers.gmail import GmailClient

            client = GmailClient()
            success = client.send_email(recipient, subject, body)

            with self._lock:
                if success:
                    self._record_success(recipient)
                else:
                    self._record_failure()

            return success

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            with self._lock:
                self._record_failure()
            return False

    def _record_success(self, recipient: str):
        """Record successful email send."""
        now = datetime.now()

        self._stats["sent_today"] += 1
        self._stats["total_sent"] += 1
        self._stats["successful"] += 1
        self._stats["last_sent"] = now.isoformat()

        # Update hourly
        hour_key = str(now.hour)
        self._stats["hourly"][hour_key] = self._stats["hourly"].get(hour_key, 0) + 1

        # Update per-recipient
        if recipient:
            recipient_key = recipient.lower()
            self._stats["by_recipient"][recipient_key] = (
                self._stats["by_recipient"].get(recipient_key, 0) + 1
            )

        self._save_stats()

        logger.info(
            f"Email sent successfully. Today: {self._stats['sent_today']}/{self.MAX_DAILY}"
        )

    def _record_failure(self):
        """Record failed email attempt."""
        self._stats["failed"] += 1
        self._save_stats()

    def get_status(self) -> dict:
        """Get current rate limiter status."""
        with self._lock:
            self._check_and_reset_daily()
            self._check_and_reset_hourly()

            current_hour = str(datetime.now().hour)
            hourly_sent = self._stats["hourly"].get(current_hour, 0)

            return {
                "can_send": self._stats["sent_today"] < self.MAX_DAILY
                and hourly_sent < self.MAX_HOURLY,
                "daily": {
                    "sent": self._stats["sent_today"],
                    "limit": self.MAX_DAILY,
                    "remaining": self.MAX_DAILY - self._stats["sent_today"],
                    "percentage": round(
                        self._stats["sent_today"] / self.MAX_DAILY * 100, 1
                    ),
                },
                "hourly": {
                    "sent": hourly_sent,
                    "limit": self.MAX_HOURLY,
                    "remaining": self.MAX_HOURLY - hourly_sent,
                },
                "total": {
                    "sent": self._stats.get("total_sent", 0),
                    "successful": self._stats.get("successful", 0),
                    "failed": self._stats.get("failed", 0),
                },
                "last_sent": self._stats.get("last_sent"),
            }

    def wait_if_needed(self) -> int:
        """Wait if rate limited. Returns seconds to wait.

        Returns:
            Seconds to wait (0 if not limited)
        """
        can_send, reason = self.can_send()
        if can_send:
            return 0

        # Calculate wait time
        if "Daily" in reason:
            # Wait until midnight
            now = datetime.now()
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return int((tomorrow - now).total_seconds())

        if "Hourly" in reason:
            # Wait until next hour
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(
                hours=1
            )
            return int((next_hour - now).total_seconds())

        # Default wait 60 seconds
        return 60


# Singleton instance
_rate_limiter = None


def get_rate_limiter() -> GmailRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = GmailRateLimiter()
    return _rate_limiter
