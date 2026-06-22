from flask import Blueprint, jsonify, request
from firebase_client import db
from google.cloud import firestore
import uuid

live_space_bp = Blueprint("live_space", __name__)

LIVE_SPACES_COLLECTION = "live_spaces"


# =========================================
# GET LIVE SPACE
# =========================================
@live_space_bp.route("/<space_id>", methods=["GET"])
def get_live_space(space_id):

    try:
        doc = db.collection(
            LIVE_SPACES_COLLECTION
        ).document(space_id).get()

        if not doc.exists:
            return jsonify({
                "error": "Live space not found"
            }), 404

        data = doc.to_dict()

        data["id"] = doc.id

        return jsonify({
            "space": data
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CREATE LIVE SPACE
# =========================================
@live_space_bp.route("/create", methods=["POST"])
def create_live_space():

    try:
        data = request.json

        space = {

            "space_id": str(uuid.uuid4()),

            "title": data.get(
                "title",
                "Untitled Space"
            ),

            "topic": data.get(
                "topic",
                "General Discussion"
            ),

            "host": data.get(
                "host",
                "NeuroAdmin"
            ),

            "listeners": 0,

            "speakers": [
                data.get(
                    "host",
                    "NeuroAdmin"
                )
            ],

            "is_live": True,

            "created_at":
                firestore.SERVER_TIMESTAMP
        }

        doc_ref = db.collection(
            LIVE_SPACES_COLLECTION
        ).document(space["space_id"])

        doc_ref.set(space)

        return jsonify({
            "message": "Live space created",
            "space": space
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# JOIN LIVE SPACE
# =========================================
@live_space_bp.route("/join/<space_id>", methods=["POST"])
def join_live_space(space_id):

    try:
        data = request.json

        username = data.get(
            "username",
            "user"
        )

        space_ref = db.collection(
            LIVE_SPACES_COLLECTION
        ).document(space_id)

        doc = space_ref.get()

        if not doc.exists:
            return jsonify({
                "error": "Space not found"
            }), 404

        space_ref.update({

            "listeners":
                firestore.Increment(1),

            "participants":
                firestore.ArrayUnion(
                    [username]
                )
        })

        updated = space_ref.get().to_dict()

        return jsonify({
            "message": f"{username} joined",
            "listeners":
                updated.get("listeners", 0)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# LEAVE LIVE SPACE
# =========================================
@live_space_bp.route("/leave/<space_id>", methods=["POST"])
def leave_live_space(space_id):

    try:
        data = request.json

        username = data.get(
            "username",
            "user"
        )

        space_ref = db.collection(
            LIVE_SPACES_COLLECTION
        ).document(space_id)

        doc = space_ref.get()

        if not doc.exists:
            return jsonify({
                "error": "Space not found"
            }), 404

        current = doc.to_dict()

        listeners = current.get(
            "listeners",
            0
        )

        if listeners > 0:

            space_ref.update({

                "listeners":
                    firestore.Increment(-1),

                "participants":
                    firestore.ArrayRemove(
                        [username]
                    )
            })

        updated = space_ref.get().to_dict()

        return jsonify({
            "message": f"{username} left",
            "listeners":
                updated.get("listeners", 0)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# END LIVE SPACE
# =========================================
@live_space_bp.route("/end/<space_id>", methods=["POST"])
def end_live_space(space_id):

    try:
        space_ref = db.collection(
            LIVE_SPACES_COLLECTION
        ).document(space_id)

        doc = space_ref.get()

        if not doc.exists:
            return jsonify({
                "error": "Space not found"
            }), 404

        space_ref.update({
            "is_live": False
        })

        return jsonify({
            "message": "Live space ended"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET ACTIVE LIVE SPACES
# =========================================
@live_space_bp.route("/active/all", methods=["GET"])
def get_active_spaces():

    try:
        docs = db.collection(
            LIVE_SPACES_COLLECTION
        ).where(
            "is_live",
            "==",
            True
        ).stream()

        spaces = []

        for doc in docs:

            data = doc.to_dict()

            data["id"] = doc.id

            spaces.append(data)

        return jsonify({
            "spaces": spaces
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
