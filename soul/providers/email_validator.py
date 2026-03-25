"""Email validation module to verify addresses exist."""

import re
import socket
import dns.resolver
from typing import List, Tuple


class EmailValidator:
    """Validate email addresses and check if they exist."""

    # Common disposable email domains to reject
    DISPOSABLE_DOMAINS = {
        "tempmail.com",
        "10minutemail.com",
        "guerrillamail.com",
        "mailinator.com",
        "throwaway.email",
        "getnada.com",
        "yopmail.com",
        "trashmail.com",
        "fakeinbox.com",
    }

    # Common typo domains for major companies
    TYPO_DOMAINS = {
        "tether.to": ["tether.io", "tether.co"],
        "coinbase.com": ["coinbaes.com", "conbase.com", "coinbse.com"],
        "binance.com": ["binanc3.com", "binancc.com", "binace.com"],
        "stripe.com": ["stripo.com", "stripe.co", "stripen.com"],
        "github.com": ["gihub.com", "githb.com", "gihub.com"],
    }

    @staticmethod
    def is_valid_format(email: str) -> bool:
        """Check if email has valid format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def get_domain(email: str) -> str:
        """Extract domain from email."""
        if "@" not in email:
            return None
        return email.split("@")[1].lower()

    @staticmethod
    def is_disposable(email: str) -> bool:
        """Check if email uses a disposable domain."""
        domain = EmailValidator.get_domain(email)
        return domain in EmailValidator.DISPOSABLE_DOMAINS

    @staticmethod
    def check_typos(email: str) -> List[str]:
        """Check for common typos in domain."""
        domain = EmailValidator.get_domain(email)
        if not domain:
            return []

        suggestions = []
        for correct, typos in EmailValidator.TYPO_DOMAINS.items():
            if domain in typos:
                suggestions.append(correct)
        return suggestions

    @staticmethod
    def verify_smtp(email: str, timeout: int = 5) -> Tuple[bool, str]:
        """
        Verify email exists via SMTP.
        Returns (is_valid, message).
        """
        domain = EmailValidator.get_domain(email)
        if not domain:
            return False, "Invalid email format"

        # Check format first
        if not EmailValidator.is_valid_format(email):
            return False, "Invalid email format"

        # Check disposable
        if EmailValidator.is_disposable(email):
            return False, "Disposable email not allowed"

        # Check typos
        typos = EmailValidator.check_typos(email)
        if typos:
            return False, f"Possible typo. Did you mean: {', '.join(typos)}?"

        # Try SMTP verification
        try:
            # Get MX records
            mx_records = dns.resolver.resolve(domain, "MX")
            mx_record = str(mx_records[0].exchange).rstrip(".")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            return False, f"Domain '{domain}' does not exist"
        except Exception as e:
            return False, f"Could not verify domain: {str(e)}"

        # Connect to SMTP and check
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(timeout)
            server.connect((mx_record, 25))

            # Read greeting
            response = server.recv(1024).decode()

            # Send HELO
            server.send(b"HELO check\r\n")
            server.recv(1024)

            # Send MAIL FROM
            server.send(b"MAIL FROM:<verify@example.com>\r\n")
            response = server.recv(1024).decode()

            # Send RCPT TO
            server.send(f"RCPT TO:<{email}>\r\n".encode())
            response = server.recv(1024).decode()

            server.send(b"QUIT\r\n")
            server.close()

            # Check response code
            if "250" in response:
                return True, "Email verified"
            elif "550" in response:
                return False, "Email does not exist"
            elif "554" in response:
                return False, "Email rejected"
            else:
                return True, "Email likely exists (verification inconclusive)"

        except socket.timeout:
            return False, "SMTP connection timed out"
        except ConnectionRefusedError:
            return False, "SMTP connection refused"
        except Exception as e:
            return False, f"SMTP error: {str(e)}"

    @staticmethod
    def validate(email: str, check_smtp: bool = True) -> Tuple[bool, str]:
        """
        Comprehensive email validation.

        Args:
            email: Email address to validate
            check_smtp: Whether to do SMTP verification

        Returns:
            (is_valid, message)
        """
        # Basic format check
        if not EmailValidator.is_valid_format(email):
            return False, "Invalid email format"

        # Check disposable
        if EmailValidator.is_disposable(email):
            return False, "Disposable email domains not allowed"

        # Check typos
        typos = EmailValidator.check_typos(email)
        if typos:
            return False, f"Possible typo. Did you mean: {', '.join(typos)}?"

        # SMTP verification (optional)
        if check_smtp:
            return EmailValidator.verify_smtp(email)

        return True, "Email format valid"


def validate_email(email: str, check_smtp: bool = True) -> Tuple[bool, str]:
    """Convenience function for email validation."""
    return EmailValidator.validate(email, check_smtp)


if __name__ == "__main__":
    import sys

    test_emails = [
        "careers@tether.to",
        "jobs@coinbase.com",
        "careers@binance.com",
        "jobs@stripe.com",
        "test@example.com",
    ]

    print("=== Email Validation Test ===\n")

    for email in test_emails:
        print(f"Checking: {email}")
        valid, message = validate_email(email, check_smtp=False)
        print(f"  Result: {valid} - {message}")

        if valid:
            valid_smtp, smtp_msg = validate_email(email, check_smtp=True)
            print(f"  SMTP: {valid_smtp} - {smtp_msg}")
        print()
