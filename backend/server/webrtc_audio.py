# ======================
# FILE: webrtc_audio.py 
# ======================

from aiortc import RTCPeerConnection
import asyncio
import time
import audioop

# =========================================
# OPTIONAL VAD (REAL IMPLEMENTATION)
# =========================================
try:
    import webrtcvad
    VAD_ENABLED = True
    vad = webrtcvad.Vad(2)  # 0-3 (2 = balanced)
except:
    VAD_ENABLED = False
    vad = None


class WebRTCAudioEngine:

    def __init__(self):

        # room_id -> {user_id -> peer}
        self.rooms = {}

        # user -> room
        self.user_room_map = {}

        # speaking state tracking
        self.speaking_state = {}

        # last activity timestamps
        self.last_active = {}
        self.audio_activity = {}

        # speaking tracking for ghost fix
        self.speaking_last_seen = {}

    # =========================================
    # ROOM INIT
    # =========================================
    def _ensure_room(self, room_id):
        if room_id not in self.rooms:
            self.rooms[room_id] = {}

    # =========================================
    # CREATE PEER
    # =========================================
    def create_peer(self, room_id, user_id):

        self._ensure_room(room_id)

        # remove old peer safely
        if user_id in self.rooms[room_id]:
            try:
                asyncio.create_task(self.rooms[room_id][user_id].close())
            except:
                pass

        pc = RTCPeerConnection()

        self.rooms[room_id][user_id] = pc
        self.user_room_map[user_id] = room_id

        now = time.time()
        self.last_active[user_id] = now
        self.audio_activity[user_id] = now
        self.speaking_last_seen[user_id] = now

        self.speaking_state[user_id] = False

        print(f"🎧 Peer created -> {user_id} in room {room_id}")

        # =========================================
        # AUDIO TRACK HANDLER
        # =========================================
        @pc.on("track")
        def on_track(track):

            if track.kind != "audio":
                return

            print(f"🎤 Audio track received from {user_id}")

            asyncio.create_task(
                self._process_audio_track(room_id, user_id, track)
            )

        return pc

    # =========================================
    # REAL VAD FUNCTION
    # =========================================
    def _is_speech(self, frame) -> bool:

        if not VAD_ENABLED:
            return True  # fallback safe mode

        try:
            audio = frame.to_ndarray()

            # Convert to mono if needed
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            # Convert float/int -> 16-bit PCM
            pcm = audio.astype("int16").tobytes()

            # WebRTC VAD requires 10/20/30ms frames
            return vad.is_speech(pcm, 48000)

        except:
            return False

    # =========================================
    # AUDIO PROCESSING
    # =========================================
    async def _process_audio_track(self, room_id, user_id, track):

        try:
            while True:

                frame = await track.recv()
                now = time.time()

                self.last_active[user_id] = now
                self.audio_activity[user_id] = now

                # =========================================
                # REAL SPEECH DETECTION
                # =========================================
                speaking = self._is_speech(frame)

                if speaking:
                    self.speaking_state[user_id] = True
                    self.speaking_last_seen[user_id] = now
                else:
                    # DO NOT instantly reset (prevents flicker)
                    if now - self.speaking_last_seen.get(user_id, 0) > 1.2:
                        self.speaking_state[user_id] = False

        except Exception as e:
            print(f"Audio track error ({user_id}):", e)

    # =========================================
    # GET PEER
    # =========================================
    def get_peer(self, room_id, user_id):
        return self.rooms.get(room_id, {}).get(user_id)

    # =========================================
    # REMOVE PEER
    # =========================================
    def remove_peer(self, user_id):

        room_id = self.user_room_map.get(user_id)

        if not room_id:
            return

        peer = self.rooms.get(room_id, {}).pop(user_id, None)

        if peer:
            try:
                asyncio.create_task(peer.close())
            except:
                pass

        self.user_room_map.pop(user_id, None)
        self.speaking_state.pop(user_id, None)
        self.last_active.pop(user_id, None)
        self.audio_activity.pop(user_id, None)
        self.speaking_last_seen.pop(user_id, None)

        print(f"🧹 Peer removed -> {user_id}")

    # =========================================
    # CLEAN ROOM
    # =========================================
    def clear_room(self, room_id):

        if room_id not in self.rooms:
            return

        for user_id, pc in list(self.rooms[room_id].items()):
            try:
                asyncio.create_task(pc.close())
            except:
                pass

        self.rooms.pop(room_id, None)

        self.user_room_map = {
            u: r for u, r in self.user_room_map.items()
            if r != room_id
        }

        self.speaking_state = {
            u: v for u, v in self.speaking_state.items()
            if u in self.user_room_map
        }

        self.last_active = {
            u: t for u, t in self.last_active.items()
            if u in self.user_room_map
        }

        self.audio_activity = {
            u: t for u, t in self.audio_activity.items()
            if u in self.user_room_map
        }

        self.speaking_last_seen = {
            u: t for u, t in self.speaking_last_seen.items()
            if u in self.user_room_map
        }

        print(f"🧹 Room cleared -> {room_id}")

    # =========================================
    # CLEAN GHOST USERS
    # =========================================
    def cleanup_inactive_users(self, timeout=5):

        now = time.time()
        to_remove = []

        # remove inactive audio users
        for user_id, last in self.audio_activity.items():
            if now - last > timeout:
                to_remove.append(user_id)

        for user in to_remove:
            self.remove_peer(user)

        # FORCE RESET SPEAKING STATE (IMPORTANT FIX)
        for user_id in list(self.speaking_state.keys()):

            last_seen = self.speaking_last_seen.get(user_id, 0)

            if now - last_seen > 1.2:
                self.speaking_state[user_id] = False

        # final safety cleanup
        for user_id in list(self.speaking_state.keys()):
            if user_id not in self.user_room_map:
                self.speaking_state.pop(user_id, None)

        if to_remove:
            print(f"🧹 Cleaned inactive users: {to_remove}")
