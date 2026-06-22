from aiohttp import web
import asyncio
import time
from aiortc import RTCPeerConnection, RTCSessionDescription

# =========================
# ACTIVE ROOMS (IMPROVED)
# =========================
ROOMS = {}  
# room_id -> {
#     "peers": set(),
#     "last_activity": timestamp
# }


# =========================
# INDEX
# =========================
async def index(request):
    return web.Response(text="Neurova WebRTC Voice Server Running")


# =========================
# GET / CREATE ROOM STRUCTURE
# =========================
def ensure_room(room_id):
    if room_id not in ROOMS:
        ROOMS[room_id] = {
            "peers": set(),
            "last_activity": time.time()
        }
    return ROOMS[room_id]


# =========================
# WEBRTC OFFER HANDLER
# =========================
async def offer(request):
    params = await request.json()

    room_id = params["room"]
    user_id = params.get("user", "anonymous")

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    pc = RTCPeerConnection()
    room = ensure_room(room_id)

    room["peers"].add(pc)
    room["last_activity"] = time.time()

    print(f"🎤 JOIN: {user_id} -> {room_id}")

    # =========================
    # CLEANUP ON DISCONNECT
    # =========================
    @pc.on("connectionstatechange")
    async def on_state_change():
        state = pc.connectionState
        print(f"🔄 {user_id} state:", state)

        if state in ["failed", "disconnected", "closed"]:
            await safe_remove_peer(room_id, pc)

    # =========================
    # TRACK HANDLING
    # =========================
    @pc.on("track")
    def on_track(track):
        print("🎧 Track received:", track.kind)

        room["last_activity"] = time.time()

        if track.kind == "audio":

            @track.on("ended")
            async def on_track_end():
                print("🔇 Track ended:", user_id)
                await safe_remove_peer(room_id, pc)

            # BROADCAST TO OTHERS
            for peer in list(room["peers"]):
                if peer != pc:
                    try:
                        peer.addTrack(track)
                    except:
                        pass

    # =========================
    # WEBRTC HANDSHAKE
    # =========================
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


# =========================
# SAFE PEER REMOVAL
# =========================
async def safe_remove_peer(room_id, pc):
    room = ROOMS.get(room_id)
    if not room:
        return

    if pc in room["peers"]:
        room["peers"].remove(pc)

    try:
        await pc.close()
    except:
        pass

    print(f"🧹 Peer removed from {room_id}")


# =========================
# CLEANUP ROOM
# =========================
async def cleanup(request):
    params = await request.json()
    room_id = params.get("room")

    room = ROOMS.get(room_id)

    if room:
        for pc in list(room["peers"]):
            try:
                await pc.close()
            except:
                pass

        ROOMS.pop(room_id, None)

    return web.json_response({"status": "cleaned"})


# =========================
# BACKGROUND ROOM CLEANER (IMPORTANT FIX)
# =========================
async def room_cleaner():
    while True:
        await asyncio.sleep(30)

        now = time.time()
        to_delete = []

        for room_id, room in ROOMS.items():
            if now - room["last_activity"] > 180:  # 3 min idle
                to_delete.append(room_id)

        for room_id in to_delete:
            print("🧹 Removing inactive room:", room_id)
            room = ROOMS.pop(room_id, None)

            if room:
                for pc in room["peers"]:
                    try:
                        await pc.close()
                    except:
                        pass


# =========================
# APP SETUP
# =========================
app = web.Application()
app.router.add_get("/", index)
app.router.add_post("/offer", offer)
app.router.add_post("/cleanup", cleanup)


# =========================
# START BACKGROUND TASK
# =========================
async def on_startup(app):
    app["cleaner"] = asyncio.create_task(room_cleaner())


app.on_startup.append(on_startup)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
