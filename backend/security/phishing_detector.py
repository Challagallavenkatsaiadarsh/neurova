# =========================================
# FILE: backend/security/phishing_detector.py
# =========================================

import re
from urllib.parse import urlparse


# =========================================
# SIMPLE TEXT DETECTOR
# =========================================
def detect_phishing(text):

    suspicious_words = [

        "verify your account",
        "free money",
        "click now",
        "urgent action",
        "bank login",
        "crypto giveaway",
        "reset password",
        "confirm identity",
        "wallet recovery",
        "limited time",
        "security alert",
        "login immediately",
        "claim reward"

    ]

    text = text.lower()

    for word in suspicious_words:

        if word in text:
            return True

    return False


# =========================================
# ADVANCED PHISHING ENGINE
# =========================================
class PhishingDetector:

    def __init__(self):

        # =========================================
        # DANGEROUS DOMAINS
        # =========================================
        self.bad_domains = [

            "fake-login.com",
            "freecrypto.net",
            "malware-site.xyz",
            "secure-wallet-login.com",
            "paypal-verification.net"

        ]

        # =========================================
        # SUSPICIOUS TLDS
        # =========================================
        self.bad_tlds = [

            ".xyz",
            ".tk",
            ".ru",
            ".gq",
            ".ml",
            ".cf"

        ]

        # =========================================
        # SHORTENERS
        # =========================================
        self.shorteners = [

            "bit.ly",
            "tinyurl.com",
            "goo.gl",
            "t.co"

        ]

    # =========================================
    # MAIN CHECK
    # =========================================
    def check_link(self, link):

        lowered = link.lower()

        parsed = urlparse(lowered)

        domain = parsed.netloc

        # =========================================
        # KNOWN BAD DOMAIN
        # =========================================
        for bad in self.bad_domains:

            if bad in domain:

                return {

                    "safe": False,

                    "warning":
                        "🚨 Known phishing domain detected"
                }

        # =========================================
        # SHORTENER DETECTION
        # =========================================
        for shortener in self.shorteners:

            if shortener in domain:

                return {

                    "safe": False,

                    "warning":
                        "⚠ Suspicious shortened URL detected"
                }

        # =========================================
        # RAW IP ADDRESS
        # =========================================
        ip_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"

        if re.search(ip_pattern, domain):

            return {

                "safe": False,

                "warning":
                    "⚠ Raw IP address phishing link detected"
            }

        # =========================================
        # TOO MANY SUBDOMAINS
        # =========================================
        if domain.count(".") > 3:

            return {

                "safe": False,

                "warning":
                    "⚠ Excessive subdomains detected"
            }

        # =========================================
        # SUSPICIOUS TLD
        # =========================================
        for tld in self.bad_tlds:

            if domain.endswith(tld):

                return {

                    "safe": False,

                    "warning":
                        "⚠ Suspicious domain extension detected"
                }

        # =========================================
        # LOGIN BAIT WORDS
        # =========================================
        bait_words = [

            "login",
            "verify",
            "secure",
            "update",
            "bank",
            "wallet",
            "password"

        ]

        for bait in bait_words:

            if bait in lowered:

                return {

                    "safe": False,

                    "warning":
                        "⚠ Credential harvesting pattern detected"
                }

        # =========================================
        # VERY LONG URL
        # =========================================
        if len(link) > 120:

            return {

                "safe": False,

                "warning":
                    "⚠ Suspiciously long URL detected"
            }

        # =========================================
        # SAFE
        # =========================================
        return {

            "safe": True,

            "warning":
                "✅ Link appears safe"
        }
