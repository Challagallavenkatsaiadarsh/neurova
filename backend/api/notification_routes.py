# =========================================
# FILE: backend/api/notification_routes.py
# =========================================

from flask import Blueprint, jsonify, request
from backend.firebase_client import db
from google.cloud import firestore
import uuid

notification_bp = Blueprint("notification", __name__)

NOTIFICATION_COLLECTION = "notifications"


# =========================================
# GET ALL NOTIFICATIONS
# =========================================
@notification_bp.route("/", methods=["GET"])
def get_notifications():

    try:

        notifications_ref = db.collection(
            NOTIFICATION_COLLECTION
        ).stream()

        notifications = []

        for doc in notifications_ref:

            data = doc.to_dict()

            data["id"] = doc.id

            # DEFAULTS
            data["verified"] = data.get(
                "verified",
                False
            )

            data["username"] = data.get(
                "username",
                "user"
            )

            data["text"] = data.get(
                "text",
                ""
            )

            notifications.append(data)

        # =========================================
        # SORT LATEST FIRST
        # =========================================
        def sort_key(x):

            ts = x.get("createdAt")

            if hasattr(ts, "timestamp"):
                return ts.timestamp()

            return 0

        notifications = sorted(
            notifications,
            key=sort_key,
            reverse=True
        )

        return jsonify({
            "notifications": notifications
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET VERIFIED NOTIFICATIONS
# =========================================
@notification_bp.route("/verified", methods=["GET"])
def get_verified_notifications():

    try:

        notifications_ref = db.collection(
            NOTIFICATION_COLLECTION
        ).where(
            "verified",
            "==",
            True
        ).stream()

        notifications = []

        for doc in notifications_ref:

            data = doc.to_dict()

            data["id"] = doc.id

            notifications.append(data)

        return jsonify({
            "notifications": notifications
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CREATE NOTIFICATION
# =========================================
@notification_bp.route("/create", methods=["POST"])
def create_notification():

    try:

        data = request.json

        notification = {

            "id": str(uuid.uuid4()),

            "username": data.get(
                "username",
                "user"
            ),

            "text": data.get(
                "text",
                ""
            ),

            "verified": data.get(
                "verified",
                False
            ),

            "type": data.get(
                "type",
                "general"
            ),

            "createdAt": firestore.SERVER_TIMESTAMP
        }

        db.collection(
            NOTIFICATION_COLLECTION
        ).add(notification)

        return jsonify({

            "message":
            "Notification created successfully",

            "notification": notification
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# DELETE NOTIFICATION
# =========================================
@notification_bp.route("/delete/<notification_id>", methods=["DELETE"])
def delete_notification(notification_id):

    try:

        db.collection(
            NOTIFICATION_COLLECTION
        ).document(
            notification_id
        ).delete()

        return jsonify({
            "message":
            "Notification deleted"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CLEAR ALL NOTIFICATIONS
# =========================================
@notification_bp.route("/clear", methods=["DELETE"])
def clear_notifications():

    try:

        docs = db.collection(
            NOTIFICATION_COLLECTION
        ).stream()

        for doc in docs:

            db.collection(
                NOTIFICATION_COLLECTION
            ).document(
                doc.id
            ).delete()

        return jsonify({
            "message":
            "All notifications cleared"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# AUTO CREATE LIKE NOTIFICATION
# =========================================
@notification_bp.route("/like", methods=["POST"])
def create_like_notification():

    try:

        data = request.json

        notification = {

            "username":
            data.get("username", "user"),

            "text":
            f"{data.get('username', 'user')} "
            f"liked your post ❤️",

            "verified": False,

            "type": "like",

            "createdAt":
            firestore.SERVER_TIMESTAMP
        }

        db.collection(
            NOTIFICATION_COLLECTION
        ).add(notification)

        return jsonify({
            "message":
            "Like notification created"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# AUTO CREATE COMMENT NOTIFICATION
# =========================================
@notification_bp.route("/comment", methods=["POST"])
def create_comment_notification():

    try:

        data = request.json

        comment_text = data.get(
            "comment",
            "Nice post!"
        )

        notification = {

            "username":
            data.get("username", "user"),

            "text":
            f"{data.get('username', 'user')} "
            f"commented: {comment_text}",

            "verified": False,

            "type": "comment",

            "createdAt":
            firestore.SERVER_TIMESTAMP
        }

        db.collection(
            NOTIFICATION_COLLECTION
        ).add(notification)

        return jsonify({
            "message":
            "Comment notification created"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# VERIFIED SYSTEM ALERT
# =========================================
@notification_bp.route("/security-alert", methods=["POST"])
def security_alert():

    try:

        data = request.json

        notification = {

            "username": "NeuroAI",

            "text":
            data.get(
                "text",
                "Security check passed 🔐"
            ),

            "verified": True,

            "type": "security",

            "createdAt":
            firestore.SERVER_TIMESTAMP
        }

        db.collection(
            NOTIFICATION_COLLECTION
        ).add(notification)

        return jsonify({
            "message":
            "Security alert created"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# TEST ROUTE
# =========================================
@notification_bp.route("/test", methods=["GET"])
def test_notifications():

    return jsonify({
        "message":
        "Notification routes working 🚀"
    })
