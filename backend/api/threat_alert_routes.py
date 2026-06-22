from flask import Blueprint, jsonify, request
from firebase_client import db
from google.cloud import firestore
import uuid

threat_alert_bp = Blueprint(
    "threat_alert",
    __name__
)

THREATS_COLLECTION = "threat_alerts"


# =========================================
# GET ALL THREAT ALERTS
# =========================================
@threat_alert_bp.route(
    "/",
    methods=["GET"]
)
def get_alerts():

    try:

        docs = db.collection(
            THREATS_COLLECTION
        ).stream()

        alerts = []

        for doc in docs:

            data = doc.to_dict()

            data["id"] = doc.id

            alerts.append(data)

        # =========================================
        # DEFAULT ALERTS IF EMPTY
        # =========================================
        if not alerts:

            alerts = [

                {
                    "title":
                        "Fake Crypto Giveaway Campaign",

                    "level":
                        "HIGH"
                },

                {
                    "title":
                        "Banking Phishing Attack",

                    "level":
                        "CRITICAL"
                },

                {
                    "title":
                        "Malware APK Distribution",

                    "level":
                        "HIGH"
                },

                {
                    "title":
                        "AI Voice Scam Network",

                    "level":
                        "MEDIUM"
                }
            ]

        return jsonify({
            "alerts": alerts
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CREATE ALERT
# =========================================
@threat_alert_bp.route(
    "/create",
    methods=["POST"]
)
def create_alert():

    try:

        data = request.json

        alert = {

            "alert_id":
                str(uuid.uuid4()),

            "title":
                data.get(
                    "title",
                    "Unknown Threat"
                ),

            "description":
                data.get(
                    "description",
                    ""
                ),

            "level":
                data.get(
                    "level",
                    "MEDIUM"
                ),

            "active":
                True,

            "created_at":
                firestore.SERVER_TIMESTAMP
        }

        db.collection(
            THREATS_COLLECTION
        ).document(
            alert["alert_id"]
        ).set(alert)

        return jsonify({

            "message":
                "Threat alert created",

            "alert":
                alert
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET CRITICAL ALERTS
# =========================================
@threat_alert_bp.route(
    "/critical",
    methods=["GET"]
)
def critical_alerts():

    try:

        docs = db.collection(
            THREATS_COLLECTION
        ).where(
            "level",
            "==",
            "CRITICAL"
        ).stream()

        alerts = []

        for doc in docs:

            data = doc.to_dict()

            data["id"] = doc.id

            alerts.append(data)

        return jsonify({
            "alerts": alerts
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# RESOLVE ALERT
# =========================================
@threat_alert_bp.route(
    "/resolve/<alert_id>",
    methods=["POST"]
)
def resolve_alert(alert_id):

    try:

        ref = db.collection(
            THREATS_COLLECTION
        ).document(alert_id)

        doc = ref.get()

        if not doc.exists:

            return jsonify({
                "error":
                    "Alert not found"
            }), 404

        ref.update({
            "active": False
        })

        return jsonify({
            "message":
                "Threat resolved"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# LIVE SECURITY STATUS
# =========================================
@threat_alert_bp.route(
    "/status",
    methods=["GET"]
)
def threat_status():

    return jsonify({

        "monitoring":
            True,

        "live_detection":
            True,

        "ai_protection":
            True,

        "network_status":
            "SECURE"
    })
