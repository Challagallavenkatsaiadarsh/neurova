from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# =========================
# DATABASE
# =========================
SPACES = {}


# =========================
# CREATE SPACE
# =========================
@app.route("/api/spaces/create", methods=["POST"])
def create_space():
    data = request.json

    space_id = str(uuid.uuid4())

    space = {
        "space_id": space_id,
        "name": data.get("name"),
        "topic": data.get("topic"),
        "host": data.get("host"),
        "created_at": str(datetime.utcnow()),
        "participants": {
            data.get("host"): "host"
        }
    }

    SPACES[space_id] = space

    return jsonify({"space": space})


# =========================
# JOIN SPACE (VOICE ROOM)
# =========================
@socketio.on("join_voice_space")
def join_voice(data):
    space_id = data["space_id"]
    user = data["user"]

    join_room(space_id)

    if user not in SPACES[space_id]["participants"]:
        SPACES[space_id]["participants"][user] = "listener"

    # broadcast updated user list
    emit("user_joined", {
        "user": user,
        "role": SPACES[space_id]["participants"][user],
        "participants": SPACES[space_id]["participants"]
    }, room=space_id)


# =========================
# WEBRTC SIGNALING: OFFER
# =========================
@socketio.on("webrtc_offer")
def webrtc_offer(data):
    emit("webrtc_offer", data, room=data["target"])


# =========================
# WEBRTC SIGNALING: ANSWER
# =========================
@socketio.on("webrtc_answer")
def webrtc_answer(data):
    emit("webrtc_answer", data, room=data["target"])


# =========================
# ICE CANDIDATES (VERY IMPORTANT)
# =========================
@socketio.on("ice_candidate")
def ice_candidate(data):
    emit("ice_candidate", data, room=data["target"])


# =========================
# LEAVE SPACE
# =========================
@socketio.on("leave_space")
def leave_space(data):
    space_id = data["space_id"]
    user = data["user"]

    leave_room(space_id)

    if user in SPACES[space_id]["participants"]:
        del SPACES[space_id]["participants"][user]

    emit("user_left", {
        "user": user,
        "participants": SPACES[space_id]["participants"]
    }, room=space_id)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
