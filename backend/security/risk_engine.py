# =========================================
# FILE: backend/security/risk_engine.py
# =========================================

from backend.security.ai_scam_detector import AIScamDetector
from backend.security.cyber_score import CyberScore
from backend.security.behavior_analyzer import BehaviorAnalyzer


class RiskEngine:

    def __init__(self):

        self.scam_detector = AIScamDetector()
        self.cyber_score = CyberScore()
        self.behavior = BehaviorAnalyzer()

        # =========================================
        # EXTRA RISK KEYWORDS
        # =========================================
        self.risky_words = [
            "hack",
            "crack",
            "bypass",
            "steal",
            "phishing"
        ]

    # =========================================
    # SIMPLE RISK CALCULATOR
    # =========================================
    def calculate_risk(self, text):

        risk = 0

        text = text.lower()

        for word in self.risky_words:

            if word in text:
                risk += 20

        return risk

    # =========================================
    # FULL RISK ANALYSIS
    # =========================================
    def full_risk_analysis(self, message):

        # =========================================
        # SCAM CHECK
        # =========================================
        scam_result = self.scam_detector.analyze_text(message)

        # =========================================
        # EXTRA RISK SCORE
        # =========================================
        risk_score = self.calculate_risk(message)

        # =========================================
        # CYBER SCORE
        # =========================================
        score_result = self.cyber_score.calculate_score(
            safe_logins=5,
            suspicious_links=1 if scam_result["is_scam"] else 0,
            reports=0,
            verified=True
        )

        # =========================================
        # USER BEHAVIOR ANALYSIS
        # =========================================
        behavior_result = self.behavior.analyze_user_behavior(
            login_count=10,
            failed_attempts=0,
            reports=0,
            suspicious_links=1 if scam_result["is_scam"] else 0
        )

        # =========================================
        # FINAL THREAT LEVEL
        # =========================================
        if risk_score >= 80:
            threat_level = "CRITICAL"

        elif risk_score >= 40:
            threat_level = "HIGH"

        elif risk_score >= 20:
            threat_level = "MEDIUM"

        else:
            threat_level = "LOW"

        # =========================================
        # FINAL RESPONSE
        # =========================================
        return {

            "scam_detection": scam_result,

            "cyber_score": score_result,

            "behavior_analysis": behavior_result,

            "risk_score": risk_score,

            "threat_level": threat_level
        }
