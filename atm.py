# improved attribute trainer

"""

Sender Email Attributes
Phishing emails often have suspicious sender addresses.

Domain Entropy: Calculate entropy of the sender’s email domain.
Domain TLD Match: Check if the domain uses less reputable TLDs (.xyz, .info, etc.).
Similarity to Known Brands: Use Levenshtein distance to compare the sender’s domain to well-known brand domains (e.g., paypa1.com vs. paypal.com).
Contains Numbers/Hyphens: Check if the email domain contains unusual numbers, dashes, or long subdomains.
Free Email Services: Flag if the domain uses free email providers like gmail.com, yahoo.com, which are sometimes used in phishing.
2. Subject Line Attributes
Subject lines in phishing emails often have patterns like urgency, keywords, or capitalization.

Keyword Presence: Check for phishing-indicative keywords like:
"Urgent," "Verify," "Account," "Suspended," "Limited," "Click here."
All Caps: Flag if the subject line is in all uppercase.
Length of Subject: Measure the length of the subject line (phishing subjects might be unusually short or long).
Punctuation Abuse: Count exclamation marks (!) or question marks (???).
Similarity to Spam Patterns: Compare subject lines to spam keywords using cosine similarity or distance metrics.
3. Email Body Content Attributes
Analyze patterns in the email body for phishing.

Keyword Frequency: Count the occurrence of phishing-related words, e.g.,:
"Login," "Password," "Account," "Verify," "Bank," "Suspended," "Click here," "Link."
URL Presence: Detect if the body contains URLs, particularly short URLs or obfuscated links.
HTML Links: Extract and analyze anchor tag (<a href>) links. Compare domains to known brand domains.
Number of Words/Characters: Compute email length. Phishing emails might have very little or excessively verbose content.
Language Complexity: Measure the readability score (e.g., Flesch-Kincaid score) of the email.
Misspellings: Count spelling errors in the body text using a dictionary or NLP tool.
Suspicious Phrases: Detect phrases like "You have won," "Confirm now," "Update your information," etc.
Attachment Flags: Check for references to attachments like “attached file,” “PDF,” “invoice,” etc.
4. Combined Attributes
Sender-Body Mismatch: If the sender domain doesn’t match the content context (e.g., an email claiming to be from "Amazon" but sent from random.xyz).
HTML Content Flag: Flag if the email body contains HTML content, as phishing emails often rely on HTML tricks.
Number of External Links: Count external links in the email body.
Similarity to Known Templates: Use vectorization (e.g., TF-IDF) and cosine similarity to compare emails to known phishing templates.

"""


import re
import math
from collections import OrderedDict, Counter
from Levenshtein import distance
import tldextract
class AttributeManager:
    """
    Attribute Manager for phishing analysis.
    Fetches data like brands, TLDs, keywords, and squatted words from a PostgreSQL database
    and computes features for email sender, subject, and body content.
    """
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

        # Fetch relevant data from database
        self.trainer_brand = self.fetch_data("SELECT brand_name FROM brand_table;")
        self.trainer_topleveldomain = self.fetch_data("SELECT tld FROM topleveldomain_table;")
        self.trainer_keyword = self.fetch_data("SELECT keyword FROM keyword_table;")
        self.trainer_squatedword = self.fetch_data("SELECT squated_word FROM squatedword_table;")

    def fetch_data(self, query):
        """
        Execute a query and return results as a list.
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def compute_attributes(self, email_data):
        """
        Compute all features for a given email.
        
        Args:
            email_data (dict): Dictionary containing sender, subject, and body.
            
        Returns:
            OrderedDict: Features computed for the given email.
        """
        attributes = OrderedDict()
        attributes.update(self.att_sender_email(email_data['sender']))
        attributes.update(self.att_subject_line(email_data['subject']))
        attributes.update(self.att_email_body(email_data['body']))
        return attributes

    # ===== Sender Email Attributes ===== #
    def att_sender_email(self, sender):
        """
        Compute features related to the sender email address.
        """
        results = OrderedDict()
        domain_data = tldextract.extract(sender)
        domain = domain_data.domain
        tld = domain_data.suffix

        # Domain entropy
        p, length = Counter(domain), len(domain)
        entropy = -sum(count / length * math.log(count / length, 2) for count in p.values())
        results['sender_domain_entropy'] = entropy

        # Suspicious TLD check
        results['suspicious_tld'] = 1 if tld in self.trainer_topleveldomain else 0

        # Similarity to known brands
        results['brand_similarity'] = any(distance(domain, brand) <= 2 for brand in self.trainer_brand)

        # Numbers and hyphens in domain
        results['contains_number'] = int(bool(re.search(r'\d', domain)))
        results['contains_hyphen'] = int('-' in domain)

        return results

    # ===== Subject Line Attributes ===== #
    def att_subject_line(self, subject):
        """
        Compute features related to the subject line.
        """
        results = OrderedDict()

        # Check if subject is all uppercase
        results['subject_all_caps'] = int(subject.isupper())

        # Subject length
        results['subject_length'] = len(subject)

        # Number of exclamation marks
        results['exclamation_count'] = subject.count('!')

        # Contains phishing keywords
        results['contains_phishing_keyword'] = any(
            kw.lower() in subject.lower() for kw in self.trainer_keyword
        )

        return results

    # ===== Email Body Content Attributes ===== #
    def att_email_body(self, body):
        """
        Compute features related to the email body.
        """
        results = OrderedDict()

        # Body length
        results['body_length'] = len(body)

        # Number of URLs
        results['url_count'] = len(re.findall(r'https?://\S+', body))

        # HTML flag
        results['html_flag'] = int(bool(re.search(r'<.*?>', body)))

        # Keyword frequency
        results['phishing_keyword_count'] = sum(
            body.lower().count(kw.lower()) for kw in self.trainer_keyword
        )

        # Squatted words detection
        squated_word_flag = any(
            distance(word, sw) <= 1 for sw in self.trainer_squatedword for word in body.split()
        )
        results['contains_squated_words'] = int(squated_word_flag)

        return results
sample_email = {
    "sender": "support@paypa1.com",
    "subject": "URGENT: Your account has been suspended!!!",
    "body": "Dear user, click here to verify your account: https://bit.ly/3random"
}

known_brands = ["paypal", "amazon", "microsoft"]
phishing_tlds = ["xyz", "info", "top"]
suspicious_keywords = ["urgent", "verify", "suspended", "click here", "update"]

attribute_manager = AttributeManager(known_brands, suspicious_keywords, phishing_tlds)
features = attribute_manager.compute_attributes(sample_email)
print(features)
