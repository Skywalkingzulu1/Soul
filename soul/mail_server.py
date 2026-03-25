"""
Andile Mail Server — Local email system with CAN-SPAM compliance.

Features:
  - 10 emails/day max (enforced)
  - CAN-SPAM compliant (physical address, unsubscribe)
  - Gmail SMTP relay for delivery
  - Local maildir for sent archive
"""

import os
import time
import json
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import message_from_string
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration — credentials from environment variables
LOCAL_SMTP_HOST = "127.0.0.1"
LOCAL_SMTP_PORT = 1025
MAILDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "maildir")
GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL", "andilexmchunu@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")

# Limits
MAX_DAILY_SENDS = 10

# CAN-SPAM compliance
PHYSICAL_ADDRESS = "Andile Sizophila Mchunu, Johannesburg, South Africa"
UNSUBSCRIBE_EMAIL = "andilexmchunu@gmail.com"


def setup_maildir() -> None:
    """Create maildir directory structure."""
    for d in ["cur", "new", "tmp", "sent"]:
        os.makedirs(os.path.join(MAILDIR, d), exist_ok=True)


def save_to_maildir(raw_email, folder="new") -> None:
    """Save an email to maildir."""
    setup_maildir()
    filename = f"{int(time.time() * 1000000)}.{os.getpid()}.eml"
    path = os.path.join(MAILDIR, folder, filename)
    with open(path, "w") as f:
        f.write(raw_email)
    return path


def get_inbox() -> None:
    """Get all emails from inbox."""
    setup_maildir()
    emails = []
    for folder in ["new", "cur"]:
        folder_path = os.path.join(MAILDIR, folder)
        if os.path.exists(folder_path):
            for f in sorted(os.listdir(folder_path)):
                if f.endswith(".eml"):
                    path = os.path.join(folder_path, f)
                    with open(path) as fh:
                        raw = fh.read()
                    try:
                        msg = message_from_string(raw)
                        emails.append(
                            {
                                "file": f,
                                "from": msg.get("From", ""),
                                "to": msg.get("To", ""),
                                "subject": msg.get("Subject", ""),
                                "body": _get_body(msg),
                            }
                        )
                    except Exception:
                        pass
    return emails


def _get_body(msg) -> None:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="replace")
    else:
        return msg.get_payload(decode=True).decode(errors="replace")
    return ""


# Daily send tracking
COUNTER_FILE = os.path.join(MAILDIR, "daily_count.json")


def _get_today() -> None:
    return datetime.now().strftime("%Y-%m-%d")


def _load_counter() -> None:
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE) as f:
                data = json.load(f)
            if data.get("date") == _get_today():
                return data.get("count", 0)
        except Exception:
            pass
    return 0


def _save_counter(count) -> None:
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    with open(COUNTER_FILE, "w") as f:
        json.dump({"date": _get_today(), "count": count}, f)


def get_daily_send_count() -> None:
    """How many emails sent today."""
    return _load_counter()


def get_remaining_sends() -> None:
    """How many emails can still be sent today."""
    return max(0, MAX_DAILY_SENDS - _load_counter())


def send_email(to, subject, body_text=None, body_html=None, sender=None) -> None:
    """Send email with daily limit and CAN-SPAM compliance.

    Raises RuntimeError if daily limit reached.
    """
    # Check daily limit
    count = _load_counter()
    if count >= MAX_DAILY_SENDS:
        raise RuntimeError(
            f"Daily send limit reached ({MAX_DAILY_SENDS}/day). Try again tomorrow."
        )

    if not sender:
        sender = f"Andile Sizophila <{GMAIL_EMAIL}>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg["Reply-To"] = UNSUBSCRIBE_EMAIL
    msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg["List-Unsubscribe"] = f"<mailto:{UNSUBSCRIBE_EMAIL}?subject=unsubscribe>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    # CAN-SPAM: append physical address and unsubscribe to body
    address_footer_text = (
        f"\n\n---\n{PHYSICAL_ADDRESS}\n"
        f"To unsubscribe, reply with 'unsubscribe' in the subject line."
    )
    address_footer_html = (
        f"<hr><p style='font-size:10px;color:#888;'>"
        f"{PHYSICAL_ADDRESS}<br>"
        f"<a href='mailto:{UNSUBSCRIBE_EMAIL}?subject=unsubscribe'>Unsubscribe</a>"
        f"</p>"
    )

    if body_text:
        msg.attach(MIMEText(body_text + address_footer_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html + address_footer_html, "html"))
    elif body_text:
        # Only text provided, no HTML
        pass  # already attached above

    # Save to local maildir
    save_to_maildir(msg.as_string(), folder="sent")

    # Deliver via Gmail SMTP
    password = GMAIL_PASSWORD or os.environ.get("GMAIL_PASSWORD", "")
    if not password:
        raise RuntimeError(
            "Gmail password not set. Set GMAIL_PASSWORD environment variable."
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=30) as server:
        server.login(GMAIL_EMAIL, password)
        server.sendmail(GMAIL_EMAIL, to, msg.as_string())

    # Update counter
    _save_counter(count + 1)
    remaining = MAX_DAILY_SENDS - (count + 1)
    logger.info(f"Email sent to {to} ({remaining} remaining today)")
    return True


if __name__ == "__main__":
    setup_maildir()
    print(f"Maildir: {MAILDIR}")
    print(f"Sent today: {get_daily_send_count()}/{MAX_DAILY_SENDS}")
    print(f"Remaining: {get_remaining_sends()}")
