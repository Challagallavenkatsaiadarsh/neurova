# =========================================
# FILE: backend/security/behavior_analyzer.py
# =========================================

from datetime import datetime


class BehaviorAnalyzer:

    def analyze_user_behavior(
        self,
        login_count,
        failed_attempts,
        reports,
        suspicious_links
    ):

        score = 0

        # SAFE LOGIN ACTIVITY
        if login_count > 5:
            score += 20

        # FAILED LOGIN ATTEMPTS
        score -= failed_attempts * 10

        # USER REPORTS
        score -= reports * 15

        # SUSPICIOUS LINKS
        score -= suspicious_links * 20

        # LIMITS
        if score < 0:
            score = 0

        if score > 100:
            score = 100

        return {
            "behavior_score": score,
            "status": self.get_status(score),
            "checked_at": str(datetime.now())
        }

    def get_status(self, score):

        if score >= 80:
            return "🟢 Trusted"

        if score >= 50:
            return "🟡 Moderate Risk"

        return "🔴 Dangerous"
