from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import uuid

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
    host = data.get("host")

    space = {
        "space_id": space_id,
        "name": data.get("name"),
        "topic": data.get("topic"),
        "host": host,
        "created_at": str(datetime.utcnow()),
        "participants": {
            host: "host"
        },
        "cohost_requests": []
    }

    SPACES[space_id] = space

    return jsonify({"status": "created", "space": space})


# =========================
# SOCKET CONNECT
# =========================
@socketio.on("connect")
def handle_connect():
    print("User connected")


# =========================
# JOIN SPACE ROOM (REAL TIME)
# =========================
@socketio.on("join_space")
def on_join(data):
    space_id = data["space_id"]
    user = data["user"]

    join_room(space_id)

    if user not in SPACES[space_id]["participants"]:
        SPACES[space_id]["participants"][user] = "listener"

    emit("space_update", SPACES[space_id], room=space_id)


# =========================
# SEND COHOST REQUEST (HOST ONLY)
# =========================
@socketio.on("cohost_request")
def cohost_request(data):
    space_id = data["space_id"]
    host = data["host"]
    to_user = data["to"]

    space = SPACES[space_id]

    if space["host"] != host:
        emit("error", {"msg": "Only host can invite cohost"})
        return

    request_obj = {
        "from": host,
        "to": to_user,
        "status": "pending"
    }

    space["cohost_requests"].append(request_obj)

    # 🔥 REAL TIME NOTIFY TARGET USER
    emit("cohost_invite", request_obj, room=space_id)


# =========================
# ACCEPT COHOST
# =========================
@socketio.on("accept_cohost")
def accept_cohost(data):
    space_id = data["space_id"]
    user = data["user"]

    space = SPACES[space_id]

    for r in space["cohost_requests"]:
        if r["to"] == user and r["status"] == "pending":
            r["status"] = "accepted"
            space["participants"][user] = "cohost"

    # 🔥 BROADCAST UPDATE
    emit("space_update", space, room=space_id)


# =========================
# DECLINE COHOST
# =========================
@socketio.on("decline_cohost")
def decline_cohost(data):
    space_id = data["space_id"]
    user = data["user"]

    space = SPACES[space_id]

    for r in space["cohost_requests"]:
        if r["to"] == user and r["status"] == "pending":
            r["status"] = "declined"

    emit("space_update", space, room=space_id)


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

    emit("space_update", SPACES[space_id], room=space_id)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
