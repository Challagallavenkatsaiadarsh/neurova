# =========================================
# FILE: backend/security/ai_scam_detector.py
# =========================================

import re


# =========================================
# QUICK SCAM DETECTOR
# =========================================
def detect_scam(text):

    scam_words = [
        "send otp",
        "win iphone",
        "urgent transfer",
        "claim reward"
    ]

    text = text.lower()

    for word in scam_words:

        if word in text:
            return True

    return False


# =========================================
# AI SCAM DETECTOR CLASS
# =========================================
class AIScamDetector:

    def __init__(self):

        self.scam_keywords = [

            # MONEY / REWARD
            "free money",
            "claim reward",
            "win iphone",
            "lottery winner",
            "double your money",

            # OTP / PASSWORD
            "send otp",
            "password reset",
            "wallet recovery",

            # PAYMENT
            "urgent payment",
            "urgent transfer",

            # CRYPTO
            "crypto giveaway",
            "investment guaranteed",

            # BANK
            "bank verification",

            # CLICKBAIT
            "click to win"
        ]

    # =========================================
    # MAIN ANALYZER
    # =========================================
    def analyze_text(self, text):

        text = text.lower()

        detected = []

        # =========================================
        # AI KEYWORD ANALYSIS
        # =========================================
        for keyword in self.scam_keywords:

            if keyword in text:
                detected.append(keyword)

        # =========================================
        # QUICK DETECTOR
        # =========================================
        quick_detection = detect_scam(text)

        # =========================================
        # RISK CALCULATION
        # =========================================
        risk_level = self.calculate_risk(
            len(detected)
        )

        return {

            "is_scam":
                len(detected) > 0 or quick_detection,

            "risk_level":
                risk_level,

            "detected_keywords":
                detected,

            "quick_detection":
                quick_detection
        }

    # =========================================
    # RISK ENGINE
    # =========================================
    def calculate_risk(self, matches):

        if matches >= 5:
            return "HIGH"

        if matches >= 2:
            return "MEDIUM"

        if matches >= 1:
            return "LOW"

        return "SAFE"

    # =========================================
    # LIVE SECURITY CHECK
    # =========================================
    def live_scan(self, text):

        result = self.analyze_text(text)

        if result["risk_level"] == "HIGH":

            return (
                "🚨 HIGH RISK SCAM DETECTED\n"
                f"Keywords: {result['detected_keywords']}"
            )

        elif result["risk_level"] == "MEDIUM":

            return (
                "⚠ Suspicious message detected\n"
                f"Keywords: {result['detected_keywords']}"
            )

        elif result["risk_level"] == "LOW":

            return (
                "🟡 Possible scam indicators found"
            )

        return "🟢 Message looks safe"
