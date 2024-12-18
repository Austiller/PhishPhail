

# Example raw email headers as text
raw_email = """\
From: "PayPal Support" <support@paypa1.com>
To: user@example.com
Subject: URGENT: Your account has been suspended!!!
Date: Wed, 18 Dec 2024 14:30:00 +0000
Message-ID: <1234@example.com>
Content-Type: text/plain; charset="UTF-8"

Dear user,

Your account has been flagged for suspicious activity. Please verify your account:
https://bit.ly/verify-now
"""
import re
from email import message_from_string, policy
from email.utils import parseaddr
from base64 import urlsafe_b64decode


class EmailMessage:
    def __init__(self, raw_email, is_base64_encoded=False):
        """
        Initialize the EmailMessage class by parsing the raw email data.

        Args:
            raw_email (str): The raw email as a string (or base64-encoded string).
            is_base64_encoded (bool): Set to True if the email is base64-encoded.
        """
        # Decode base64-encoded email if necessary
        if is_base64_encoded:
            raw_email = urlsafe_b64decode(raw_email).decode("utf-8")

        # Parse the email using the email library
        self.msg = message_from_string(raw_email, policy=policy.default)

        # Extract common headers
        self.sender = self._parse_sender(self.msg['From'])
        self.recipient = self._parse_recipient(self.msg['To'])
        self.subject = self.msg['Subject']
        self.date = self.msg['Date']
        self.message_id = self.msg['Message-ID']
        self.reply_to = self._parse_recipient(self.msg['Reply-To']) if self.msg['Reply-To'] else None

        # Extract the email body
        self.body = self._extract_body(self.msg)

        # Extract links from the body
        self.links = self._extract_links(self.body)

    @staticmethod
    def _parse_sender(sender_header):
        """
        Parse the sender's email and name from the "From" header.
        """
        sender_name, sender_email = parseaddr(sender_header)
        return {"name": sender_name, "email": sender_email}

    @staticmethod
    def _parse_recipient(recipient_header):
        """
        Parse the recipient's email and name from the "To" or "Reply-To" header.
        """
        recipient_name, recipient_email = parseaddr(recipient_header)
        return {"name": recipient_name, "email": recipient_email}

    @staticmethod
    def _extract_body(msg):
        """
        Extract the plain-text body from the email.
        """
        if msg.is_multipart():
            # Iterate through parts to find plain-text content
            for part in msg.iter_parts():
                if part.get_content_type() == "text/plain":
                    return part.get_content()
        else:
            # Single-part email
            return msg.get_body(preferencelist=('plain')).get_content()
        return ""

    @staticmethod
    def _extract_links(body):
        """
        Extract all URLs from the email body using regular expressions.
        """
        if body:
            return re.findall(r'https?://[^\s]+', body)
        return []

    def __repr__(self):
        """
        Return a string representation of the email object for debugging.
        """
        return (
            f"EmailMessage(sender={self.sender}, recipient={self.recipient}, "
            f"subject={self.subject}, date={self.date}, links={self.links})"
        )

