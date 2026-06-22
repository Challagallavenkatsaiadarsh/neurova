# =========================================
# FILE: backend/api/auth_routes.py
# =========================================

import random
from flask import Blueprint, request, jsonify
from backend.firebase_client import db

from backend.security.device_fingerprint import get_device_id
from backend.security.anomaly_detector import detect_login_anomaly
from backend.security.cyber_score import CyberScore

from datetime import datetime

auth_bp = Blueprint("auth", __name__)
cyber_score = CyberScore()


# =========================================
# SIGNUP USER
# =========================================
@auth_bp.route("/signup", methods=["POST"])
def signup():

    try:
        data = request.json or {}

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()

        print("\n📝 SIGNUP REQUEST")
        print("USERNAME:", username)
        print("EMAIL:", email)

        # =========================================
        # VALIDATION
        # =========================================
        if not username or not email or not password:
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        # =========================================
        # CHECK EXISTING EMAIL
        # =========================================
        users = db.collection("users").stream()

        for doc in users:

            user = doc.to_dict()

            existing_email = str(
                user.get("email", "")
            ).strip().lower()

            if existing_email == email:
                return jsonify({
                    "success": False,
                    "message": "Email already registered"
                }), 409

        # =========================================
        # CREATE USER DOCUMENT
        # =========================================
        user_data = {
            "username": username,
            "email": email,
            "password": password,

            "cyber_score": 100,
            "security_status": "Safe",

            "joined_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),

            # Onboarding fields
            "date_of_birth": "",
            "user_id_handle": "",
            "onboarding_completed": False,

            # Profile fields
            "bio": "",
            "profile_picture": "",
            "banner_picture": "",

            # Security fields
            "last_device_id": "",
            "verified": False
        }

        new_user = db.collection("users").add(
            user_data
        )

        user_id = new_user[1].id

        print(
            "✅ USER CREATED:",
            user_id
        )

        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "user_id": user_id
        }), 201

    except Exception as e:

        print(
            "🔥 SIGNUP ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================================
# USERNAME SUGGESTIONS (NEW API)
# =========================================
@auth_bp.route("/username-suggestions", methods=["POST"])
def username_suggestions():
    import random

    try:
        data = request.json or {}

        full_name = (data.get("username") or "").strip().lower()

        if not full_name:
            return jsonify({
                "success": False,
                "message": "Name required"
            }), 400

        parts = full_name.split()

        first = parts[0] if len(parts) > 0 else "user"
        middle = parts[1] if len(parts) > 1 else ""
        last = parts[-1] if len(parts) > 2 else ""

        suggestions = []

        # smart @ handles
        if middle and last:
            suggestions.append(f"@{middle}_{last}")
            suggestions.append(f"@{first}_{last}")
            suggestions.append(f"@{first[0]}{last}")
        else:
            suggestions.append(f"@{first}_{last}")
            suggestions.append(f"@real_{first}")
            suggestions.append(f"@{first}{random.randint(10,99)}")

        suggestions = list(dict.fromkeys(suggestions))[:3]

        return jsonify({
            "success": True,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
# =========================================
# LOGIN USER
# =========================================
@auth_bp.route("/login", methods=["POST"])
def login():

    try:
        data = request.json or {}

        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()

        print("\n🔐 LOGIN REQUEST RECEIVED")
        print("EMAIL INPUT:", email)

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400

        user = None
        user_id = None

        print("\n📡 SCANNING FIREBASE USERS...\n")

        users_ref = db.collection("users").stream()

        for doc in users_ref:

            u = doc.to_dict()

            db_email = str(
                u.get("email", "")
            ).strip().lower()

            print("➡ FIREBASE EMAIL:", db_email)

            if db_email == email:
                user = u
                user_id = doc.id
                print("✅ USER MATCH FOUND")
                break

        if not user:
            print("❌ USER NOT FOUND IN FIREBASE")

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        stored_password = str(
            user.get("password", "")
        ).strip()

        if stored_password != password:
            print("❌ PASSWORD MISMATCH")

            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        print("✅ LOGIN SUCCESS")

        device_id = get_device_id()
        anomaly = detect_login_anomaly(email, device_id)

        score_result = cyber_score.calculate_score(
            safe_logins=1 if not anomaly else 0,
            suspicious_links=1 if anomaly else 0,
            reports=0,
            verified=True
        )

        db.collection("users").document(user_id).update({
            "last_device_id": device_id,
            "cyber_score": score_result["score"],
            "security_status": score_result["status"]
        })

        return jsonify({
            "success": True,
            "message": "Login successful",
            "needs_onboarding": not user.get(
            "onboarding_completed",
            False
        ),
            "user": {
                "id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "cyber_score": score_result["score"],
                "security_status": score_result["status"]
            },
            "security": {
                "device_id": device_id,
                "anomaly_detected": anomaly
            }
        })

    except Exception as e:

        print("🔥 LOGIN ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================================
# COMPLETE ONBOARDING
# =========================================
@auth_bp.route("/complete-onboarding", methods=["POST"])
def complete_onboarding():

    try:
        data = request.json or {}

        user_id = data.get("user_id")
        date_of_birth = (
            data.get("date_of_birth") or ""
        ).strip()

        user_id_handle = (
            data.get("user_id_handle") or ""
        ).strip()

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID required"
            }), 400

        if not date_of_birth:
            return jsonify({
                "success": False,
                "message": "Date of birth required"
            }), 400

        if not user_id_handle:
            return jsonify({
                "success": False,
                "message": "User handle required"
            }), 400

        users = db.collection("users").stream()

        for doc in users:

            user = doc.to_dict()

            existing_handle = str(
                user.get(
                    "user_id_handle",
                    ""
                )
            ).strip().lower()

            if existing_handle == user_id_handle.lower():
                return jsonify({
                    "success": False,
                    "message": "User ID already taken"
                }), 409

        db.collection("users").document(user_id).update({
            "date_of_birth": date_of_birth,
            "user_id_handle": user_id_handle,
            "onboarding_completed": True
        })

        return jsonify({
            "success": True,
            "message": "Onboarding completed"
        })

    except Exception as e:

        print(
            "🔥 ONBOARDING ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================================
# SESSION CHECK
# =========================================
@auth_bp.route("/session/<user_id>", methods=["GET"])
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
# LOGOUT
# =========================================
@auth_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "success": True,
        "message": "Logout successful"
    })
