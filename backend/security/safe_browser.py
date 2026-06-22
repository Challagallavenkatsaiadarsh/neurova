# =========================================
# FILE: backend/security/safe_browser.py
# =========================================

import webbrowser
import validators


class SafeBrowser:

    def __init__(self):

        self.blocked_domains = [
            "malware",
            "phishing",
            "hack",
            "darkweb",
            "scam"
        ]

    # =========================================
    # OPEN URL SAFELY
    # =========================================
    def open_url(self, url):

        try:

            # AUTO HTTPS
            if not url.startswith("http"):
                url = "https://" + url

            # URL VALIDATION
            if not validators.url(url):
                return "❌ Invalid URL"

            lowered = url.lower()

            # BLOCK DANGEROUS DOMAINS
            for bad in self.blocked_domains:

                if bad in lowered:

                    return (
                        "🚫 Dangerous domain blocked"
                    )

            # OPEN SAFELY
            webbrowser.open(url)

            return (
                f"✅ Safe Opening:\n{url}"
            )

        except Exception as e:

            return f"❌ Browser Error: {e}"
