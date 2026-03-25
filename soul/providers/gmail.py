import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from soul.core.config import config, identity
from soul.core.logger import setup_logger

logger = setup_logger(__name__)

class GmailClient:
    """Native Gmail client via IMAP/SMTP."""
    
    def __init__(self):
        self.email_address = identity.email
        self.password = config.gmail_app_password

    def send_email(self, recipient, subject, body):
        """Send an email via SMTP."""
        if not self.password:
            logger.error("GMAIL_APP_PASSWORD not set.")
            return False
            
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = recipient

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email_address, self.password)
                server.send_message(msg)
                logger.info(f"Email sent to {recipient}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def check_inbox(self, limit=5):
        """Check the latest emails via IMAP."""
        if not self.password:
            logger.error("GMAIL_APP_PASSWORD not set.")
            return []

        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.password)
            mail.select('inbox')

            _, data = mail.search(None, 'ALL')
            mail_ids = data[0].split()
            
            results = []
            for i in mail_ids[-limit:]:
                _, msg_data = mail.fetch(i, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg['subject']
                        from_ = msg['from']
                        results.append({"subject": subject, "from": from_})
            
            mail.logout()
            return results
        except Exception as e:
            logger.error(f"Failed to check inbox: {e}")
            return []
