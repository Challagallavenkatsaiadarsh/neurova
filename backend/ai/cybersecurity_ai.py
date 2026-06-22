# =========================================
# FILE: backend/ai/cybersecurity_ai.py
# =========================================

class CyberSecurityAI:

    def analyze_link(self, link):

        if "http" in link:
            return "Link appears valid."

        return "Invalid link detected."
