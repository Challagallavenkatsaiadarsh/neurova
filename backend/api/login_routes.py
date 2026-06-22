# =========================================
# FILE: backend/api/login_routes.py
# =========================================

from flask import Blueprint, request, jsonify

from backend.database.firebase_client import db
from backend.security.device_fingerprint import get_device_id
from backend.security.anomaly_detector import detect_login_anomaly
from backend.security.cyber_score import CyberScore

login_bp = Blueprint("login", __name__)
cyber_score = CyberScore()


# =========================================
# LOGIN USER
# =========================================
@login_bp.route("/login", methods=["POST"])
def login():

    try:
        data = request.json

        # =========================================
        # DEBUG INPUT
        # =========================================
        print("\n================ LOGIN REQUEST ================")
        print("RAW DATA:", data)

        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()

        print("NORMALIZED EMAIL:", email)
        print("INPUT PASSWORD:", password)

        # =========================================
        # VALIDATION
        # =========================================
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400

        # =========================================
        # FIND USER (SAFE SCAN + DEBUG)
        # =========================================
        users = db.collection("users").stream()

        user = None
        user_id = None

        print("\n================ FIREBASE SCAN ================")

        for doc in users:
            data = doc.to_dict()

            db_email = str(data.get("email", "")).strip().lower()
            db_password = str(data.get("password", "")).strip()

            print("CHECKING DOC:", doc.id)
            print("DB EMAIL:", db_email)
            print("DB PASSWORD:", db_password)

            if db_email == email:
                user = data
                user_id = doc.id
                break

        # =========================================
        # USER NOT FOUND
        # =========================================
        if not user:
            print("RESULT: USER NOT FOUND")
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # =========================================
        # PASSWORD CHECK
        # =========================================
        stored_password = str(user.get("password", "")).strip()

        print("\n================ PASSWORD CHECK ================")
        print("STORED PASSWORD:", stored_password)
        print("INPUT PASSWORD:", password)

        if stored_password != password:
            print("RESULT: INVALID PASSWORD")
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        print("RESULT: LOGIN SUCCESS")

        # =========================================
        # DEVICE ID
        # =========================================
        device_id = get_device_id()

        # =========================================
        # LOGIN ANOMALY
        # =========================================
        anomaly = detect_login_anomaly(email, device_id)

        # =========================================
        # CYBER SCORE
        # =========================================
        score_result = cyber_score.calculate_score(
            safe_logins=1 if not anomaly else 0,
            suspicious_links=1 if anomaly else 0,
            reports=0,
            verified=True
        )

        # =========================================
        # SAVE LOGIN INFO
        # =========================================
        db.collection("users").document(user_id).update({
            "last_device_id": device_id,
            "cyber_score": score_result["score"],
            "security_status": score_result["status"]
        })

        # =========================================
        # SUCCESS RESPONSE
        # =========================================
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "verified": user.get("verified", False),
                "cyber_score": score_result["score"],
                "security_status": score_result["status"]
            },
            "security": {
                "anomaly_detected": anomaly,
                "device_id": device_id
            }
        })

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# CHECK USER SESSION
# =========================================
@login_bp.route("/session/<user_id>", methods=["GET"])
def check_session(user_id):

    try:
        doc = db.collection("users").document(user_id).get()

        if not doc.exists:
            return jsonify({
                "success": False,
                "message": "Session not found"
            }), 404

        user = doc.to_dict()

        return jsonify({
            "success": True,
            "session": {
                "user_id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "cyber_score": user.get("cyber_score", 100),
                "security_status": user.get("security_status", "Safe")
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# LOGOUT USER
# =========================================
@login_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "success": True,
        "message": "Logout successful"
    })
