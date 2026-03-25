"""Email module — unified interface for sending and receiving.

Uses the local mail server (Gmail relay) for sending.
Uses mail.tm for disposable email creation.
"""

import logging
import time
from soul.mail_server import (
    send_email as _send_email,
    get_inbox,
    setup_maildir,
    LOCAL_SMTP_HOST,
    LOCAL_SMTP_PORT,
)

logger = logging.getLogger(__name__)

# Re-export from mail_server
send_email = _send_email
get_local_inbox = get_inbox


class DisposableEmail:
    """Create temporary email addresses via mail.tm API."""

    def __init__(self) -> None:
        self.address = None
        self.password = None
        self.token = None
        self.domain = None

    def create(self, username=None) -> None:
        import requests, random, string

        API = "https://api.mail.tm"
        r = requests.get(f"{API}/domains", timeout=15)
        domains = r.json().get("hydra:member", [])
        if not domains:
            raise RuntimeError("No mail.tm domains available")

        self.domain = domains[0]["domain"]
        if not username:
            username = "andile" + "".join(random.choices(string.digits, k=5))
        self.address = f"{username}@{self.domain}"
        self.password = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )

        r = requests.post(
            f"{API}/accounts",
            json={
                "address": self.address,
                "password": self.password,
            },
            timeout=15,
        )
        r.raise_for_status()

        r = requests.post(
            f"{API}/token",
            json={
                "address": self.address,
                "password": self.password,
            },
            timeout=15,
        )
        if r.status_code == 200:
            self.token = r.json().get("token")

        return self.address

    def get_messages(self) -> None:
        import requests

        if not self.token:
            return []
        r = requests.get(
            "https://api.mail.tm/messages",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=15,
        )
        return r.json().get("hydra:member", [])

    def wait_for_message(self, timeout=120, poll_interval=5) -> None:
        import requests

        start = time.time()
        while time.time() - start < timeout:
            msgs = self.get_messages()
            if msgs:
                r = requests.get(
                    f"https://api.mail.tm/messages/{msgs[0]['id']}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=15,
                )
                return r.json()
            time.sleep(poll_interval)
        return None

    def extract_verification_code(self, message) -> None:
        import re

        if not message:
            return None
        body = message.get("text", "") or ""
        html = message.get("html", [""]) or [""]
        if isinstance(html, list):
            html = html[0] if html else ""
        text = f"{body} {html}"
        codes = re.findall(r"(?<!\d)(\d{6})(?!\d)", text)
        if not codes:
            codes = re.findall(r"(?<!\d)(\d{4})(?!\d)", text)
        return codes[0] if codes else None
