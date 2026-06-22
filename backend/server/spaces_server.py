# ==============================
# FILE: space_server.py (LIVEKIT ARCHITECTURE)
# ==============================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.ai.live_spaces_engine import LiveSpacesEngine
from backend.ai.livekit_token_service import LiveKitTokenService

app = FastAPI()

engine = LiveSpacesEngine()
livekit = LiveKitTokenService()

connections = {}


# ==============================
# BROADCAST HELPER
# ==============================
async def broadcast(space_id: str, message: dict):

    if space_id not in connections:
        return

    dead = []

    for ws in connections[space_id]:
        try:
            await ws.send_json(message)
        except:
            dead.append(ws)

    for ws in dead:
        try:
            connections[space_id].remove(ws)
        except:
            pass


# ==============================
# WEBSOCKET (CONTROL ONLY)
# ==============================
@app.websocket("/space/{space_id}")
async def space_socket(websocket: WebSocket, space_id: str):

    await websocket.accept()

    if space_id not in connections:
        connections[space_id] = []

    connections[space_id].append(websocket)

    user = None

    try:

        # init room state
        engine.create_space(space_id, host="system")

        await broadcast(space_id, {
            "type": "system",
            "message": f"Space {space_id} is live"
        })

        while True:

            data = await websocket.receive_json()

            action = data.get("type")
            user = data.get("user", "anonymous")

            # =========================
            # JOIN → LIVEKIT TOKEN
            # =========================
            if action == "join":

                engine.join(space_id, user)

                token_data = livekit.create_token(
                    room=space_id,
                    user=user,
                    is_speaker=True
                )

                await broadcast(space_id, {
                    "type": "join",
                    "user": user,
                    "livekit": token_data
                })

            # =========================
            # CHAT ONLY (NO AUDIO HERE)
            # =========================
            elif action == "message":

                engine.send_message(space_id, user, data.get("message"))

                await broadcast(space_id, {
                    "type": "message",
                    "user": user,
                    "message": data.get("message")
                })

            # =========================
            # REACTIONS
            # =========================
            elif action == "react":

                engine.react(space_id, user, data.get("emoji"))

                await broadcast(space_id, {
                    "type": "react",
                    "user": user,
                    "emoji": data.get("emoji")
                })

            # =========================
            # RAISE HAND
            # =========================
            elif action == "raise_hand":

                engine.request_speak(space_id, user)

                await broadcast(space_id, {
                    "type": "raise_hand",
                    "user": user
                })

            # =========================
            # SPEAKER APPROVAL
            # =========================
            elif action == "approve_speaker":

                target = data.get("target_user")

                engine.approve_speaker(space_id, user, target)

                await broadcast(space_id, {
                    "type": "speaker_approved",
                    "user": target
                })

            # =========================
            # MUTE / CONTROL ONLY
            # =========================
            elif action == "mute_speaker":

                target = data.get("target_user")

                engine.mute_user(space_id, user, target)

                await broadcast(space_id, {
                    "type": "mute",
                    "target": target
                })

    except WebSocketDisconnect:

        if websocket in connections.get(space_id, []):
            connections[space_id].remove(websocket)

        if user:
            engine.leave(space_id, user)

            await broadcast(space_id, {
                "type": "leave",
                "user": user
            })

    finally:

        if websocket in connections.get(space_id, []):
            connections[space_id].remove(websocket)

        if user:
            engine.leave(space_id, user)
