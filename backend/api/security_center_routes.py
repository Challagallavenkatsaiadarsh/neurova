from flask import Blueprint, jsonify, request

from backend.security.cyber_score import CyberScore
from backend.security.link_scanner import scan_link
from backend.security.phishing_detector import detect_phishing
from backend.security.ai_scam_detector import detect_scam

security_center_bp = Blueprint(
    "security_center",
    __name__
)

# =========================================
# ENGINES
# =========================================
cyber_engine = CyberScore()


# =========================================
# GET SECURITY FEATURES
# =========================================
@security_center_bp.route(
    "/features",
    methods=["GET"]
)
def get_features():

    try:

        features = [

            {
                "title":
                    "Safe Link Sandbox",
                "icon":
                    "🔗",
                "active":
                    True
            },

            {
                "title":
                    "AI Scam Detection",
                "icon":
                    "🧠",
                "active":
                    True
            },

            {
                "title":
                    "Device Fingerprinting",
                "icon":
                    "📱",
                "active":
                    True
            },

            {
                "title":
                    "Threat Alerts",
                "icon":
                    "🚨",
                "active":
                    True
            },

            {
                "title":
                    "Cyber Shield Score",
                "icon":
                    "🛡",
                "active":
                    True
            },

            {
                "title":
                    "Account Takeover Protection",
                "icon":
                    "🔐",
                "active":
                    True
            }
        ]

        return jsonify({
            "features": features
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SECURITY HEALTH CHECK
# =========================================
@security_center_bp.route(
    "/health",
    methods=["GET"]
)
def security_health():

    try:

        return jsonify({

            "status": "ACTIVE",

            "systems": {

                "safe_browser": True,

                "phishing_detector": True,

                "scam_detection": True,

                "threat_monitoring": True,

                "cyber_shield": True,

                "account_protection": True
            }
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SECURITY SCAN
# =========================================
@security_center_bp.route(
    "/scan",
    methods=["POST"]
)
def security_scan():

    try:

        data = request.json

        text = data.get("text", "")

        threats = []

        # =========================================
        # PHISHING CHECK
        # =========================================
        phishing = detect_phishing(text)

        if phishing:

            threats.append(
                "Possible phishing detected"
            )

        # =========================================
        # SCAM CHECK
        # =========================================
        scam = detect_scam(text)

        if scam:

            threats.append(
                "Possible scam detected"
            )

        # =========================================
        # LINK CHECK
        # =========================================
        if "http://" in text or "https://" in text:

            result = scan_link(text)

            if result == "danger":

                threats.append(
                    "Dangerous link detected"
                )

        # =========================================
        # CYBER SCORE
        # =========================================
        score = cyber_engine.calculate_score(

            safe_logins=1,

            suspicious_links=len(threats),

            reports=0,

            verified=True
        )

        return jsonify({

            "safe":
                len(threats) == 0,

            "threats":
                threats,

            "score":
                score["score"],

            "status":
                score["status"]
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET CYBER SCORE
# =========================================
@security_center_bp.route(
    "/cyber_score",
    methods=["GET"]
)
def get_cyber_score():

    try:

        result = cyber_engine.calculate_score(

            safe_logins=12,

            suspicious_links=1,

            reports=0,

            verified=True
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
