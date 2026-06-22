# =========================================
# FILE: backend/security/link_scanner.py (DEBUG VERSION)
# =========================================

import re
from urllib.parse import urlparse

from backend.security.phishing_detector import detect_phishing
from backend.security.sandbox_engine import SandboxEngine


# =========================================
# SAFE DOMAIN WHITELIST
# =========================================
SAFE_DOMAINS = {
    "google.com",
    "www.google.com",
    "youtube.com",
    "www.youtube.com",
    "wikipedia.org",
    "github.com",
    "www.github.com",
    "openai.com",
    "microsoft.com",
    "apple.com",
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com"
}


# =========================================
# EXTRACT URLS
# =========================================
def extract_links(text):
    url_pattern = r"(https?://[^\s]+)"
    links = re.findall(url_pattern, text)
    print(f"[LINK_SCANNER] Extracted links: {links}")
    return links


# =========================================
# DOMAIN CHECK
# =========================================
def is_safe_domain(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().strip()
        domain = domain.split(":")[0]

        print(f"[LINK_SCANNER] Checking domain: {domain}")

        for safe in SAFE_DOMAINS:
            if domain == safe or domain.endswith("." + safe):
                print(f"[LINK_SCANNER] SAFE MATCH FOUND → {domain} matches {safe}")
                return True

        print(f"[LINK_SCANNER] NOT IN WHITELIST → {domain}")
        return False

    except Exception as e:
        print(f"[LINK_SCANNER] DOMAIN PARSE ERROR: {e}")
        return False


# =========================================
# MAIN SCANNER
# =========================================
def scan_link(text):

    print("\n========== LINK SCAN START ==========")
    print(f"[INPUT TEXT] {text}")

    links = extract_links(text.lower())

    if not links:
        print("[RESULT] No links found → SAFE")
        return "safe"

    for link in links:

        print(f"\n[SCANNING LINK] {link}")

        # STEP 1: SAFE DOMAIN CHECK
        if is_safe_domain(link):
            print("[RESULT] SAFE DOMAIN → SKIPPING SECURITY SCAN")
            continue

        # STEP 2: PHISHING CHECK
        try:
            phishing = detect_phishing(link)
            print(f"[PHISHING CHECK] {phishing}")

            if phishing:
                print("[RESULT] PHISHING DETECTED → DANGER")
                return "danger"

        except Exception as e:
            print(f"[PHISHING ERROR] {e}")

        # STEP 3: KEYWORD CHECK
        suspicious_keywords = [
            "login", "verify", "free", "bonus",
            "crypto", "wallet", "bank", "password"
        ]

        if any(k in link.lower() for k in suspicious_keywords):
            print("[RESULT] SUSPICIOUS KEYWORDS FOUND → DANGER")
            return "danger"

    print("[FINAL RESULT] SAFE")
    return "safe"


# =========================================
# CLASS VERSION (DEBUG)
# =========================================
class LinkScanner:

    def __init__(self):
        self.sandbox = SandboxEngine()

    def extract_links(self, text):
        links = re.findall(r"(https?://[^\s]+)", text)
        print(f"[CLASS SCANNER] Extracted: {links}")
        return links

    def scan_message(self, text):

        print("\n========== CLASS SCAN ==========")

        links = self.extract_links(text)

        phishing_text_detected = detect_phishing(text)

        print(f"[TEXT PHISHING] {phishing_text_detected}")

        results = []

        for link in links:

            print(f"[CLASS SCAN LINK] {link}")

            domain_safe = is_safe_domain(link)

            print(f"[DOMAIN SAFE?] {domain_safe}")

            results.append({
                "url": link,
                "domain_scan": "safe" if domain_safe else "unknown",
                "phishing": False,
                "sandbox": self.sandbox.preview_link(link),
                "text_phishing_detected": phishing_text_detected
            })

        if not links:
            print("[CLASS SCAN] No links found")

            results.append({
                "url": None,
                "domain_scan": "safe",
                "phishing": False,
                "sandbox": {"preview": "No links"},
                "text_phishing_detected": phishing_text_detected
            })

        return results
