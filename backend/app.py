from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from datetime import datetime
from threading import Thread
import time

# =========================
# OPTIONAL DB LAYER (SAFE IMPORT)
# =========================
try:
    from db import Database
    DB_ENABLED = True
except:
    DB_ENABLED = False


# =========================
# APP INIT
# =========================
app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)


# =========================
# IN-MEMORY CACHE (REALTIME LAYER)
# =========================
SPACES = {}


# =========================
# HELPERS
# =========================
def can_join_stage(space):
    return len(space.get("speakers", [])) < 5


def is_host(space, user):
    return space.get("host") == user


def is_cohost(space, user):
    return user in space.get("cohosts", [])


def is_moderator(space, user):
    return is_host(space, user) or is_cohost(space, user)


# =========================
# DB HELPERS (OPTIONAL)
# =========================
async def save_space_to_db(space):
    if not DB_ENABLED:
        return
    try:
        await Database.execute(
            "INSERT INTO spaces(id, name, topic, host) VALUES (%s, %s, %s, %s)",
            space["space_id"], space["name"], space["topic"], space["host"]
        )
    except:
        pass


# =========================
# CREATE SPACE
# =========================
@app.route("/api/spaces/create", methods=["POST"])
def create_space():
    data = request.json

    name = data.get("name")
    topic = data.get("topic")
    host = data.get("host")

    if not name or not host:
        return jsonify({"error": "name and host required"}), 400

    space_id = str(uuid.uuid4())

    space = {
        "space_id": space_id,
        "name": name,
        "topic": topic,
        "host": host,

        # roles
        "cohosts": [],

        # live state
        "participants": [],
        "speakers": [],
        "raised_hands": [],
        "muted_users": [],
        "kicked_users": [],
        "speak_requests": [],

        # LIVE AUDIO STATE
        "active_speaker": None,
        "speaking_users": {},   # user -> volume level

        "created_at": str(datetime.utcnow())
    }

    SPACES[space_id] = space

    if DB_ENABLED:
        Thread(target=lambda: __import__("asyncio").run(save_space_to_db(space))).start()

    return jsonify({"space": space})


# =========================
# GET SPACES
# =========================
@app.route("/api/spaces", methods=["GET"])
def get_spaces():
    return jsonify({"spaces": list(SPACES.values())})


# =========================
# GET SPACE
# =========================
@app.route("/api/spaces/<space_id>", methods=["GET"])
def get_space(space_id):
    space = SPACES.get(space_id)
    if not space:
        return jsonify({"error": "space not found"}), 404
    return jsonify(space)


# =========================
# SOCKET JOIN / LEAVE
# =========================
@socketio.on("join_room")
def handle_join(data):
    room = data.get("room")
    user = data.get("user")

    join_room(room)

    emit("room_joined", {"room": room, "user": user}, room=room)


@socketio.on("leave_room")
def handle_leave(data):
    room = data.get("room")
    user = data.get("user")

    leave_room(room)

    emit("room_left", {"room": room, "user": user}, room=room)


# =========================
# JOIN SPACE (REST)
# =========================
@app.route("/api/spaces/join/<space_id>", methods=["POST"])
def join_space(space_id):

    user = request.json.get("user")

    space = SPACES.get(space_id)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if user in space["kicked_users"]:
        return jsonify({"error": "user was kicked"}), 403

    if user not in space["participants"]:
        space["participants"].append(user)

    socketio.emit("participant_update", space, room=space_id)

    return jsonify({"status": "joined"})


# =========================
# RAISE HAND
# =========================
@app.route("/api/spaces/raise-hand", methods=["POST"])
def raise_hand():

    user = request.json.get("user")
    room = request.json.get("room")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if user not in space["raised_hands"]:
        space["raised_hands"].append(user)

    socketio.emit("hand_update", space, room=room)

    return jsonify({"status": "hand_raised"})


# =========================
# MUTE (HOST/COHOST ONLY)
# =========================
@app.route("/api/spaces/mute", methods=["POST"])
def mute_user():

    room = request.json.get("room")
    target = request.json.get("target")
    actor = request.json.get("actor")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if not is_moderator(space, actor):
        return jsonify({"error": "not allowed"}), 403

    if target not in space["muted_users"]:
        space["muted_users"].append(target)

    socketio.emit("mute_event", {"room": room, "user": target}, room=room)

    return jsonify({"status": "muted"})


# =========================
# KICK (HOST/COHOST ONLY)
# =========================
@app.route("/api/spaces/kick", methods=["POST"])
def kick_user():

    room = request.json.get("room")
    target = request.json.get("target")
    actor = request.json.get("actor")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if not is_moderator(space, actor):
        return jsonify({"error": "not allowed"}), 403

    if target in space["participants"]:
        space["participants"].remove(target)

    space["kicked_users"].append(target)

    socketio.emit("kick_event", {"room": room, "user": target}, room=room)

    return jsonify({"status": "kicked"})


# =========================
# PROMOTE SPEAKER
# =========================
@app.route("/api/spaces/promote", methods=["POST"])
def promote_user():

    room = request.json.get("room")
    target = request.json.get("target")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if can_join_stage(space) and target not in space["speakers"]:
        space["speakers"].append(target)

    if target in space["raised_hands"]:
        space["raised_hands"].remove(target)

    socketio.emit("speaker_update", space, room=room)

    return jsonify({"status": "promoted"})


# =========================
# COHOST PROMOTE
# =========================
@app.route("/api/spaces/promote-cohost", methods=["POST"])
def promote_cohost():

    room = request.json.get("room")
    target = request.json.get("target")
    actor = request.json.get("actor")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    if not is_host(space, actor):
        return jsonify({"error": "only host can promote cohost"}), 403

    if target not in space["cohosts"]:
        space["cohosts"].append(target)

    socketio.emit("cohost_update", {"room": room, "user": target}, room=room)

    return jsonify({"status": "cohost_promoted"})


# =========================
# REQUEST SPEAK
# =========================
@app.route("/api/spaces/request-speak", methods=["POST"])
def request_speak():

    data = request.json
    room = data.get("room")
    user = data.get("user")

    space = SPACES.get(room)

    if not space:
        return jsonify({"error": "space not found"}), 404

    space["speak_requests"].append({
        "user": user,
        "status": "pending",
        "time": str(datetime.utcnow())
    })

    socketio.emit("speak_request_update", space, room=room)

    return jsonify({"status": "request_sent"})


# =========================
# LIVE SPEAKING INDICATOR
# =========================
@socketio.on("speaking")
def handle_speaking(data):

    room = data.get("room")
    user = data.get("user")
    is_speaking = data.get("is_speaking", False)
    volume = data.get("volume", 0)

    space = SPACES.get(room)

    if not space:
        return

    if is_speaking:
        space["active_speaker"] = user
        space["speaking_users"][user] = volume
    else:
        space["speaking_users"].pop(user, None)

        if space["active_speaker"] == user:
            space["active_speaker"] = None

    socketio.emit("live_speaking", {
        "room": room,
        "user": user,
        "is_speaking": is_speaking,
        "volume": volume
    }, room=room)


# =========================
# PUSH TO TALK SYSTEM
# =========================
@socketio.on("start_talk")
def start_talk(data):
    room = data.get("room")
    user = data.get("user")

    socketio.emit("ptt_start", {"room": room, "user": user}, room=room)


@socketio.on("stop_talk")
def stop_talk(data):
    room = data.get("room")
    user = data.get("user")

    socketio.emit("ptt_stop", {"room": room, "user": user}, room=room)


# =========================
# CLEANUP INACTIVE ROOMS (FIXED)
# =========================
def cleanup_spaces():
    while True:
        time.sleep(60)

        now = datetime.utcnow()
        to_delete = []

        for space_id, space in list(SPACES.items()):
            try:
                created = datetime.fromisoformat(space["created_at"])

                if (now - created).seconds > 7200:
                    to_delete.append(space_id)

                # =========================
                # ✅ FIX: CLEAN speaking_users
                # =========================
                space["speaking_users"] = {
                    u: v for u, v in space["speaking_users"].items()
                    if u in space["participants"]
                }

            except:
                continue

        for sid in to_delete:
            del SPACES[sid]
            print("🧹 Removed inactive space:", sid)


Thread(target=cleanup_spaces, daemon=True).start()


# =========================
# HEALTH
# =========================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "spaces": len(SPACES)
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("🚀 NEXT-GEN CLUBHOUSE BACKEND RUNNING")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
