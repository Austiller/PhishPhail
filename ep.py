import email
from email.policy import default

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

# Parse the raw email
msg = email.message_from_string(raw_email, policy=default)

# Extract headers
sender = msg['From']
recipient = msg['To']
subject = msg['Subject']
date = msg['Date']

# Extract body (if available)
if msg.is_multipart():
    for part in msg.iter_parts():
        if part.get_content_type() == "text/plain":
            body = part.get_content()
else:
    body = msg.get_body(preferencelist=('plain')).get_content()

# Print extracted data
print("Sender:", sender)
print("Recipient:", recipient)
print("Subject:", subject)
print("Date:", date)
print("Body:", body)
