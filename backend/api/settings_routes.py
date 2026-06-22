# =========================================
# FILE: backend/api/settings_routes.py
# =========================================

from flask import Blueprint, jsonify, request
from firebase_client import db

settings_bp = Blueprint("settings", __name__)

SETTINGS_COLLECTION = "settings"


# =========================================
# GET USER SETTINGS
# =========================================
@settings_bp.route("/<username>", methods=["GET"])
def get_settings(username):

    try:

        doc = db.collection(
            SETTINGS_COLLECTION
        ).document(username).get()

        # =========================================
        # DEFAULT SETTINGS
        # =========================================
        default_settings = {

            "username": username,

            "cybersecurity": {
                "phishing_detection": True,
                "link_scanner": True,
                "auto_block_links": True,
                "threat_alerts": True
            },

            "notifications": {
                "push_notifications": True,
                "threat_notifications": True,
                "email_notifications": False
            },

            "ai": {
                "enable_ai": True,
                "fast_response": True,
                "ai_memory": False
            },

            "ui": {
                "dark_mode": True,
                "reduce_animations": False
            }
        }

        # =========================================
        # CREATE DEFAULT SETTINGS
        # =========================================
        if not doc.exists:

            db.collection(
                SETTINGS_COLLECTION
            ).document(username).set(
                default_settings
            )

            return jsonify(default_settings)

        return jsonify(doc.to_dict())

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# UPDATE USERNAME
# =========================================
@settings_bp.route("/change-username", methods=["POST"])
def change_username():

    try:

        data = request.json

        old_username = data.get("old_username")
        new_username = data.get("new_username")

        if not old_username or not new_username:

            return jsonify({
                "error": "Username required"
            }), 400

        old_ref = db.collection(
            SETTINGS_COLLECTION
        ).document(old_username)

        old_doc = old_ref.get()

        if not old_doc.exists:

            return jsonify({
                "error": "User settings not found"
            }), 404

        settings_data = old_doc.to_dict()

        settings_data["username"] = new_username

        # CREATE NEW DOC
        db.collection(
            SETTINGS_COLLECTION
        ).document(new_username).set(
            settings_data
        )

        # DELETE OLD DOC
        old_ref.delete()

        return jsonify({
            "message": "Username updated",
            "new_username": new_username
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CHANGE PASSWORD
# =========================================
@settings_bp.route("/change-password", methods=["POST"])
def change_password():

    try:

        data = request.json

        username = data.get("username")
        new_password = data.get("new_password")

        if not username or not new_password:

            return jsonify({
                "error": "Missing fields"
            }), 400

        # =========================================
        # DEMO ONLY
        # =========================================
        # In production:
        # use Firebase Authentication
        # with hashed passwords
        # =========================================

        return jsonify({
            "message": "Password updated successfully"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# UPDATE CYBERSECURITY SETTINGS
# =========================================
@settings_bp.route("/cybersecurity/<username>", methods=["POST"])
def update_cybersecurity(username):

    try:

        data = request.json

        db.collection(
            SETTINGS_COLLECTION
        ).document(username).update({

            "cybersecurity.phishing_detection":
                data.get("phishing_detection", True),

            "cybersecurity.link_scanner":
                data.get("link_scanner", True),

            "cybersecurity.auto_block_links":
                data.get("auto_block_links", True),

            "cybersecurity.threat_alerts":
                data.get("threat_alerts", True)
        })

        return jsonify({
            "message": "Cybersecurity settings updated"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# UPDATE NOTIFICATION SETTINGS
# =========================================
@settings_bp.route("/notifications/<username>", methods=["POST"])
def update_notifications(username):

    try:

        data = request.json

        db.collection(
            SETTINGS_COLLECTION
        ).document(username).update({

            "notifications.push_notifications":
                data.get("push_notifications", True),

            "notifications.threat_notifications":
                data.get("threat_notifications", True),

            "notifications.email_notifications":
                data.get("email_notifications", False)
        })

        return jsonify({
            "message": "Notification settings updated"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# UPDATE AI SETTINGS
# =========================================
@settings_bp.route("/ai/<username>", methods=["POST"])
def update_ai(username):

    try:

        data = request.json

        db.collection(
            SETTINGS_COLLECTION
        ).document(username).update({

            "ai.enable_ai":
                data.get("enable_ai", True),

            "ai.fast_response":
                data.get("fast_response", True),

            "ai.ai_memory":
                data.get("ai_memory", False)
        })

        return jsonify({
            "message": "AI settings updated"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# UPDATE UI SETTINGS
# =========================================
@settings_bp.route("/ui/<username>", methods=["POST"])
def update_ui(username):

    try:

        data = request.json

        db.collection(
            SETTINGS_COLLECTION
        ).document(username).update({

            "ui.dark_mode":
                data.get("dark_mode", True),

            "ui.reduce_animations":
                data.get("reduce_animations", False)
        })

        return jsonify({
            "message": "UI settings updated"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# LOGOUT
# =========================================
@settings_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "message": "Logged out successfully"
    })


# =========================================
# SETTINGS HEALTH TEST
# =========================================
@settings_bp.route("/test", methods=["GET"])
def test_settings():

    return jsonify({
        "message": "Settings API Working 🚀"
    })
