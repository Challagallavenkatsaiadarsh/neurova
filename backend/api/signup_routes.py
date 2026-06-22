# =========================================
# FILE: backend/api/signup_routes.py
# =========================================

from flask import Blueprint, request, jsonify
from backend.database.firebase_client import db
from google.cloud import firestore   # ✅ FIX ADDED

signup_bp = Blueprint(
    "signup",
    __name__
)


# =========================================
# SIGNUP USER
# =========================================
@signup_bp.route(
    "/signup",
    methods=["POST"]
)
def signup():

    try:

        data = request.json

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # =========================================
        # VALIDATION
        # =========================================
        if not username or not email or not password:

            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        # =========================================
        # CHECK EXISTING EMAIL (FIXED SAFETY)
        # =========================================
        existing = db.collection(
            "users"
        ).where(
            "email",
            "==",
            email
        ).get()

        if len(existing) > 0:

            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 400

        # =========================================
        # USER DATA
        # =========================================
        user_data = {

            "username": username,
            "email": email,

            # ⚠️ NOTE: still plain password (ok for dev, not production)
            "password": password,

            "followers": [],
            "following": [],

            "verified": False,
            "cyber_score": 100,

            "profile_pic": "",
            "bio": "",

            "created_at": firestore.SERVER_TIMESTAMP
        }

        # =========================================
        # SAVE USER
        # =========================================
        doc_ref = db.collection(
            "users"
        ).document()

        doc_ref.set(user_data)

        return jsonify({

            "success": True,
            "message": "Signup successful",

            "user_id": doc_ref.id,

            "user": {
                "username": username,
                "email": email
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# GET USER
# =========================================
@signup_bp.route(
    "/user/<user_id>",
    methods=["GET"]
)
def get_user(user_id):

    try:

        doc = db.collection(
            "users"
        ).document(user_id).get()

        if not doc.exists:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "user": doc.to_dict()
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# UPDATE USER
# =========================================
@signup_bp.route(
    "/update/<user_id>",
    methods=["PUT"]
)
def update_user(user_id):

    try:

        data = request.json

        db.collection(
            "users"
        ).document(user_id).update(data)

        return jsonify({
            "success": True,
            "message": "User updated successfully"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
