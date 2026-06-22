# =========================================
# FILE: backend/api/spaces_routes.py
# =========================================

from flask import Blueprint, jsonify, request
from backend.firebase_client import db
from google.cloud import firestore
import uuid
from datetime import datetime
import os
import jwt   # ✅ Standard JWT encoder for clean cross-platform token formatting
import time  # ✅ Required for token timestamp constraints

spaces_bp = Blueprint("spaces", __name__)

SPACES_COLLECTION = "spaces"

# =========================================
# LIVEKIT SERVER CONFIGURATION
# =========================================
# Hardcoded to perfectly match your running Docker instance configuration
LIVEKIT_API_KEY = "devkey"
LIVEKIT_API_SECRET = "secret"
LIVEKIT_URL = "ws://127.0.0.1:7880"


def generate_livekit_token(room_name: str, identity: str, is_host: bool = False) -> str:
    """Generates a raw, perfectly formatted LiveKit Access Token JWT."""
    current_time = int(time.time())
    
    # Precise claims schema required by LiveKit's engine without broken object nesting
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "name": identity,
        "nbf": current_time - 2,           # Pre-date slightly to safely ignore tiny clock desyncs
        "exp": current_time + (60 * 60),    # Valid for 1 hour
        "video": {
            "roomCreate": is_host,
            "roomJoin": True,
            "room": room_name,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True
        }
    }
    
    # Encode with strict header specifications and standard HMAC processing
    token = jwt.encode(
        payload, 
        LIVEKIT_API_SECRET, 
        algorithm="HS256", 
        headers={"alg": "HS256", "typ": "JWT"}
    )
    
    return token


# =========================================
# GET ALL SPACES
# =========================================
@spaces_bp.route("/", methods=["GET"])
def get_spaces():
    try:
        spaces_ref = db.collection(SPACES_COLLECTION).stream()
        spaces = []

        for doc in spaces_ref:
            data = doc.to_dict()
            data["id"] = doc.id
            data["name"] = data.get("name", "Untitled Space")
            data["topic"] = data.get("topic", "General")
            data["host"] = data.get("host", "NeuroAdmin")
            data["listeners"] = data.get("listeners", 0)
            data["active"] = data.get("active", True)
            spaces.append(data)

        def sort_key(x):
            ts = x.get("createdAt")
            if isinstance(ts, str):
                return ts
            return ""

        spaces = sorted(spaces, key=sort_key, reverse=True)
        return jsonify({"spaces": spaces})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# CREATE SPACE
# =========================================
@spaces_bp.route("/create", methods=["POST"])
def create_space():
    try:
        data = request.json

        name = data.get("name", "").strip()
        topic = data.get("topic", "").strip()
        host = data.get("host", "NeuroAdmin")

        if not name:
            return jsonify({"error": "Space name required"}), 400

        space_id = str(uuid.uuid4())

        # Generate fresh LiveKit Token structural block for the room creator
        token = generate_livekit_token(room_name=space_id, identity=host, is_host=True)

        space = {
            "id": space_id,
            "name": name,
            "topic": topic,
            "host": host,
            "listeners": 1,  # Creator joins immediately
            "speakers": [host],
            "joined_users": [host],
            "active": True,
            "createdAt": datetime.utcnow().isoformat()
        }

        db.collection(SPACES_COLLECTION).document(space_id).set(space)

        # Append LiveKit structural parameters directly to JSON return block
        return jsonify({
            "message": "Space created successfully",
            "space": space,
            "livekit": {
                "url": LIVEKIT_URL,
                "token": token
            },
            "user": host
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# JOIN SPACE
# =========================================
@spaces_bp.route("/join/<space_id>", methods=["POST"])
def join_space(space_id):
    try:
        data = request.json
        username = data.get("username", "user")

        space_ref = db.collection(SPACES_COLLECTION).document(space_id)
        doc = space_ref.get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        space_data = doc.to_dict()
        joined_users = space_data.get("joined_users", [])

        if username not in joined_users:
            space_ref.update({
                "joined_users": firestore.ArrayUnion([username]),
                "listeners": firestore.Increment(1)
            })

        # Generate a distinct LiveKit entry token signed for this specific user
        token = generate_livekit_token(room_name=space_id, identity=username, is_host=False)
        updated = space_ref.get().to_dict()

        # Inject real LiveKit engine credentials back to frontend
        return jsonify({
            "message": "Joined space successfully",
            "listeners": updated.get("listeners", 0),
            "livekit": {
                "url": LIVEKIT_URL,
                "token": token
            },
            "user": username
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# LEAVE SPACE
# =========================================
@spaces_bp.route("/leave/<space_id>", methods=["POST"])
def leave_space(space_id):
    try:
        data = request.json
        username = data.get("username", "user")

        space_ref = db.collection(SPACES_COLLECTION).document(space_id)
        doc = space_ref.get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        space_data = doc.to_dict()
        joined_users = space_data.get("joined_users", [])

        if username in joined_users:
            space_ref.update({
                "joined_users": firestore.ArrayRemove([username]),
                "listeners": firestore.Increment(-1)
            })

        updated = space_ref.get().to_dict()
        return jsonify({
            "message": "Left space successfully",
            "listeners": updated.get("listeners", 0)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# END SPACE
# =========================================
@spaces_bp.route("/end/<space_id>", methods=["POST"])
def end_space(space_id):
    try:
        space_ref = db.collection(SPACES_COLLECTION).document(space_id)
        doc = space_ref.get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        space_ref.update({"active": False})
        return jsonify({"message": "Space ended"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# GET SINGLE SPACE
# =========================================
@spaces_bp.route("/<space_id>", methods=["GET"])
def get_single_space(space_id):
    try:
        doc = db.collection(SPACES_COLLECTION).document(space_id).get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        data = doc.to_dict()
        data["id"] = doc.id
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# ADD SPEAKER
# =========================================
@spaces_bp.route("/speaker/<space_id>", methods=["POST"])
def add_speaker(space_id):
    try:
        data = request.json
        username = data.get("username", "user")

        space_ref = db.collection(SPACES_COLLECTION).document(space_id)
        doc = space_ref.get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        space_ref.update({
            "speakers": firestore.ArrayUnion([username])
        })
        return jsonify({"message": "Speaker added"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# REMOVE SPEAKER
# =========================================
@spaces_bp.route("/remove-speaker/<space_id>", methods=["POST"])
def remove_speaker(space_id):
    try:
        data = request.json
        username = data.get("username", "user")

        space_ref = db.collection(SPACES_COLLECTION).document(space_id)
        doc = space_ref.get()

        if not doc.exists:
            return jsonify({"error": "Space not found"}), 404

        space_ref.update({
            "speakers": firestore.ArrayRemove([username])
        })
        return jsonify({"message": "Speaker removed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# TEST ROUTE
# =========================================
@spaces_bp.route("/test", methods=["GET"])
def test_spaces():
    return jsonify({
        "message": "Neurova Spaces backend working 🚀"
    })
