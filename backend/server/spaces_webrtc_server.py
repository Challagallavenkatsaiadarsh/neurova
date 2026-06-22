from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import time
import asyncio
from collections import defaultdict

app = FastAPI()

# =========================================
# ROOM STORAGE (IMPROVED)
# =========================================
rooms = defaultdict(list)

room_users = defaultdict(dict)

# user metadata:
# {
#   "connected": True,
#   "last_seen": timestamp,
#   "speaking": False,
#   "last_talk": timestamp
# }

# =========================================
# CONFIG
# =========================================
ICE_SERVERS = [
    {
        "urls": ["stun:stun.l.google.com:19302"]
    }
]

print("🟣 WEBRTC AI SIGNALING SERVER READY")


# =========================================
# MAIN SOCKET
# =========================================
@app.websocket("/webrtc/{room_id}")
async def webrtc_socket(websocket: WebSocket, room_id: str):

    await websocket.accept()

    user_id = None
    rooms[room_id].append(websocket)

    print(f"🟢 Connected: {room_id}")

    try:

        await websocket.send_text(json.dumps({
            "type": "ice_servers",
            "servers": ICE_SERVERS
        }))

        while True:

            data = await websocket.receive_text()
            msg = json.loads(data)

            signal_type = msg.get("type")
            user_id = msg.get("user", "anonymous")

            now = time.time()

            # =================================
            # UPDATE USER HEARTBEAT
            # =================================
            room_users[room_id][user_id] = {
                "connected": True,
                "last_seen": now,
                "speaking": room_users[room_id].get(user_id, {}).get("speaking", False),
                "last_talk": room_users[room_id].get(user_id, {}).get("last_talk", 0)
            }

            # =================================
            # JOIN
            # =================================
            if signal_type == "join":

                await broadcast(room_id, {
                    "type": "user_joined",
                    "user": user_id
                })

            # =================================
            # OFFER
            # =================================
            elif signal_type == "offer":
                await relay(room_id, websocket, {
                    "type": "offer",
                    "sdp": msg.get("sdp"),
                    "user": user_id
                })

            # =================================
            # ANSWER
            # =================================
            elif signal_type == "answer":
                await relay(room_id, websocket, {
                    "type": "answer",
                    "sdp": msg.get("sdp"),
                    "user": user_id
                })

            # =================================
            # ICE
            # =================================
            elif signal_type == "candidate":
                await relay(room_id, websocket, {
                    "type": "candidate",
                    "candidate": msg.get("candidate"),
                    "user": user_id
                })

            # =================================
            # TALKING STATE (FIXED)
            # =================================
            elif signal_type == "talking":

                active = msg.get("active", False)

                room_users[room_id][user_id]["speaking"] = active
                room_users[room_id][user_id]["last_talk"] = now

                await broadcast(room_id, {
                    "type": "talking",
                    "user": user_id,
                    "active": active
                })

            # =================================
            # MESSAGE
            # =================================
            elif signal_type == "message":

                await broadcast(room_id, {
                    "type": "message",
                    "user": user_id,
                    "text": msg.get("text", "")
                })

    except WebSocketDisconnect:

        print(f"🔴 Disconnected: {room_id}")

        await cleanup_user(room_id, user_id, websocket)

    except Exception as e:

        print("WebRTC Error:", e)

        await cleanup_user(room_id, user_id, websocket)


# =========================================
# CLEAN USER (IMPORTANT FIX)
# =========================================
async def cleanup_user(room_id, user_id, websocket):

    if websocket in rooms[room_id]:
        rooms[room_id].remove(websocket)

    if user_id and user_id in room_users[room_id]:
        del room_users[room_id][user_id]

    await broadcast(room_id, {
        "type": "user_left",
        "user": user_id
    })


# =========================================
# BROADCAST
# =========================================
async def broadcast(room_id, message):

    dead = []

    for ws in rooms.get(room_id, []):

        try:
            await ws.send_text(json.dumps(message))
        except:
            dead.append(ws)

    for d in dead:
        if d in rooms[room_id]:
            rooms[room_id].remove(d)


# =========================================
# RELAY
# =========================================
async def relay(room_id, sender, message):

    dead = []

    for ws in rooms.get(room_id, []):

        if ws == sender:
            continue

        try:
            await ws.send_text(json.dumps(message))
        except:
            dead.append(ws)

    for d in dead:
        if d in rooms[room_id]:
            rooms[room_id].remove(d)


# =========================================
# BACKGROUND CLEANUP (VERY IMPORTANT)
# =========================================
async def cleanup_loop():

    while True:
        await asyncio.sleep(5)

        now = time.time()

        for room_id in list(room_users.keys()):

            for user_id in list(room_users[room_id].keys()):

                user = room_users[room_id][user_id]

                # ❌ REMOVE STALE USERS
                if now - user["last_seen"] > 10:
                    print("🧹 Removing stale user:", user_id)

                    del room_users[room_id][user_id]

                    await broadcast(room_id, {
                        "type": "user_left",
                        "user": user_id
                    })

                # ❌ FORCE STOP STALE SPEAKING
                if user.get("speaking") and now - user["last_talk"] > 3:
                    room_users[room_id][user_id]["speaking"] = False

                    await broadcast(room_id, {
                        "type": "talking",
                        "user": user_id,
                        "active": False
                    })


# =========================================
# START BACKGROUND TASK
# =========================================
@app.on_event("startup")
async def startup():
    asyncio.create_task(cleanup_loop())


# =========================================
# HEALTH
# =========================================
@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Neurova X Spaces WebRTC Server",
        "rooms": len(rooms)
    }
