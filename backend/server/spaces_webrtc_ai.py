# =========================================
# FILE: backend/server/spaces_webrtc_ai.py
# =========================================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import json

app = FastAPI()

# =========================================
# CORS
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROOM STORAGE
# =========================================
rooms = {}

# =========================================
# USER SOCKET MAP
# =========================================
user_rooms = {}

# =========================================
# LIVE STATE (NEW FIXES)
# =========================================
room_participants = {}      # room_id -> set(users)
room_speaking_users = {}    # room_id -> {user: volume}

print("🟣 NEUROVA WEBRTC SIGNALING SERVER READY")


# =========================================
# HOME
# =========================================
@app.get("/")
async def home():
    return {
        "status": "running",
        "server": "Neurova WebRTC AI Spaces"
    }


# =========================================
# WEBRTC SOCKET
# =========================================
@app.websocket("/rtc/{room_id}")
async def rtc_socket(websocket: WebSocket, room_id: str):

    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = []

    if room_id not in room_participants:
        room_participants[room_id] = set()

    if room_id not in room_speaking_users:
        room_speaking_users[room_id] = {}

    rooms[room_id].append(websocket)

    current_user = None

    print(f"🟢 SOCKET CONNECTED -> ROOM {room_id}")

    try:

        while True:

            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except:
                continue

            msg_type = data.get("type")
            user = data.get("user")

            if user:
                current_user = user
                user_rooms[user] = room_id
                room_participants[room_id].add(user)

            # =================================
            # OFFER
            # =================================
            if msg_type == "offer":

                await broadcast(room_id, {
                    "type": "offer",
                    "sdp": data.get("sdp"),
                    "user": user
                }, exclude=websocket)

            # =================================
            # ANSWER
            # =================================
            elif msg_type == "answer":

                await broadcast(room_id, {
                    "type": "answer",
                    "sdp": data.get("sdp"),
                    "user": user
                }, exclude=websocket)

            # =================================
            # ICE
            # =================================
            elif msg_type == "ice":

                await broadcast(room_id, {
                    "type": "ice",
                    "candidate": data.get("candidate"),
                    "user": user
                }, exclude=websocket)

            # =================================
            # JOIN
            # =================================
            elif msg_type == "join":

                await broadcast(room_id, {
                    "type": "join",
                    "user": user
                })

            # =================================
            # MESSAGE
            # =================================
            elif msg_type == "message":

                await broadcast(room_id, {
                    "type": "message",
                    "user": user,
                    "message": data.get("message")
                })

            # =================================
            # REACTION
            # =================================
            elif msg_type == "reaction":

                await broadcast(room_id, {
                    "type": "reaction",
                    "user": user,
                    "emoji": data.get("emoji")
                })

            # =================================
            # RAISE HAND
            # =================================
            elif msg_type == "raise_hand":

                await broadcast(room_id, {
                    "type": "raise_hand",
                    "user": user
                })

            # =================================
            # SPEAKER APPROVAL
            # =================================
            elif msg_type == "speaker_approved":

                await broadcast(room_id, {
                    "type": "speaker_approved",
                    "user": data.get("target")
                })

            # =================================
            # TALKING STATE (FIXED)
            # =================================
            elif msg_type == "talking":

                active = data.get("active", False)
                volume = data.get("volume", 0.0)

                if active:
                    room_speaking_users[room_id][user] = volume
                else:
                    room_speaking_users[room_id].pop(user, None)

                await broadcast(room_id, {
                    "type": "talking",
                    "user": user,
                    "active": active,
                    "volume": volume
                })

    except WebSocketDisconnect:

        print(f"🔴 DISCONNECTED -> {current_user}")

    except Exception as e:
        print("SERVER ERROR:", e)

    finally:

        # =================================
        # CLEAN SOCKET
        # =================================
        try:
            rooms[room_id].remove(websocket)
        except:
            pass

        # =================================
        # CLEAN USER STATE (IMPORTANT FIX)
        # =================================
        if current_user:

            room_participants[room_id].discard(current_user)
            room_speaking_users[room_id].pop(current_user, None)

            user_rooms.pop(current_user, None)

            await broadcast(room_id, {
                "type": "leave",
                "user": current_user
            })


# =========================================
# BROADCAST
# =========================================
async def broadcast(room_id, message, exclude=None):

    if room_id not in rooms:
        return

    dead = []

    for ws in rooms[room_id]:

        if ws == exclude:
            continue

        try:
            await ws.send_text(json.dumps(message))
        except:
            dead.append(ws)

    for d in dead:
        try:
            rooms[room_id].remove(d)
        except:
            pass


# =========================================
# ACTIVE ROOMS API
# =========================================
@app.get("/rooms")
async def get_rooms():

    result = {}

    for room_id, sockets in rooms.items():

        result[room_id] = {
            "connections": len(sockets),
            "participants": len(room_participants.get(room_id, [])),
            "speaking_users": room_speaking_users.get(room_id, {})
        }

    return result
