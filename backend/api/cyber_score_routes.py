# =========================================
# FILE: backend/api/cyber_score_routes.py
# =========================================

from flask import Blueprint, jsonify, request

from backend.security.cyber_score import CyberScore

cyber_score_bp = Blueprint(
    "cyber_score",
    __name__
)

engine = CyberScore()


# =========================================
# GET CYBER SCORE
# =========================================
@cyber_score_bp.route(
    "/calculate",
    methods=["POST"]
)
def calculate_cyber_score():

    try:

        data = request.json

        result = engine.calculate_score(

            safe_logins=data.get(
                "safe_logins",
                0
            ),

            suspicious_links=data.get(
                "suspicious_links",
                0
            ),

            reports=data.get(
                "reports",
                0
            ),

            verified=data.get(
                "verified",
                False
            )
        )

        return jsonify({

            "score": result["score"],
            "status": result["status"]

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# DEMO TEST ROUTE
# =========================================
@cyber_score_bp.route(
    "/test",
    methods=["GET"]
)
def cyber_score_test():

    result = engine.calculate_score(

        safe_logins=12,
        suspicious_links=1,
        reports=0,
        verified=True
    )

    return jsonify({

        "message": "Cyber Score API Working 🚀",

        "data": result
    })
