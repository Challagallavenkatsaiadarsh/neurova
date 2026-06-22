# =========================================
# FILE: backend/security/cyber_score.py
# =========================================


class CyberScore:

    def __init__(self):

        self.last_updated_user = None
        self.last_score = 0

    # =========================================
    # MAIN SCORE CALCULATION
    # =========================================
    def calculate_score(
        self,
        safe_logins=0,
        suspicious_links=0,
        reports=0,
        verified=True
    ):

        score = 100

        # =========================================
        # RISK REDUCTION
        # =========================================
        score -= suspicious_links * 20
        score -= reports * 10

        if not verified:
            score -= 15

        # =========================================
        # SAFE ACTIVITY BONUS
        # =========================================
        score += safe_logins * 2

        # =========================================
        # LIMITS
        # =========================================
        if score > 100:
            score = 100

        if score < 0:
            score = 0

        status = self.get_status(score)

        return {
            "score": score,
            "status": status
        }

    # =========================================
    # STATUS LEVEL
    # =========================================
    def get_status(self, score):

        if score >= 80:
            return "🟢 Safe"

        if score >= 50:
            return "🟡 Risk"

        return "🔴 Dangerous"

    # =========================================
    # UPDATE SCORE SYSTEM
    # =========================================
    def update_score(self, username, value):

        self.last_updated_user = username
        self.last_score = value

        print(
            f"🛡 Cyber Score Updated for "
            f"{username}: {value}"
        )


# =========================================
# GLOBAL SCORE CALCULATOR
# =========================================
def calculate_score(
    safe_login=True,
    suspicious_links=0,
    reports=0,
    verified=True
):

    cyber = CyberScore()

    result = cyber.calculate_score(
        safe_logins=1 if safe_login else 0,
        suspicious_links=suspicious_links,
        reports=reports,
        verified=verified
    )

    return result


# =========================================
# SIMPLE FUNCTION VERSION
# =========================================
def update_score(username, value):

    print(
        f"🛡 Cyber Score Updated for "
        f"{username}: {value}"
    )
