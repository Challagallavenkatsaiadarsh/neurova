# =========================================
# FILE: backend/security/threat_feed.py
# =========================================

from datetime import datetime


class ThreatFeed:

    def __init__(self):

        self.threats = [

            {
                "title":
                    "⚠ Fake Crypto Giveaway Scam",

                "severity":
                    "HIGH",

                "category":
                    "Crypto Scam",

                "time":
                    datetime.now().strftime("%H:%M")
            },

            {
                "title":
                    "⚠ Banking Phishing Attack",

                "severity":
                    "CRITICAL",

                "category":
                    "Phishing",

                "time":
                    datetime.now().strftime("%H:%M")
            },

            {
                "title":
                    "⚠ AI Voice Scam Campaign",

                "severity":
                    "HIGH",

                "category":
                    "Voice Scam",

                "time":
                    datetime.now().strftime("%H:%M")
            },

            {
                "title":
                    "⚠ Malware APK Distribution",

                "severity":
                    "HIGH",

                "category":
                    "Malware",

                "time":
                    datetime.now().strftime("%H:%M")
            }
        ]

    # =========================================
    # GET ALL THREATS
    # =========================================
    def get_latest_threats(self):

        return self.threats

    # =========================================
    # ADD THREAT
    # =========================================
    def add_threat(
        self,
        title,
        severity="MEDIUM",
        category="General"
    ):

        self.threats.insert(
            0,
            {
                "title": title,
                "severity": severity,
                "category": category,
                "time":
                    datetime.now().strftime("%H:%M")
            }
        )

    # =========================================
    # CLEAR THREATS
    # =========================================
    def clear_threats(self):

        self.threats.clear()

    # =========================================
    # THREAT COUNT
    # =========================================
    def threat_count(self):

        return len(self.threats)

    # =========================================
    # GET CRITICAL THREATS
    # =========================================
    def get_critical_threats(self):

        return [

            threat

            for threat in self.threats

            if threat["severity"] == "CRITICAL"
        ]
