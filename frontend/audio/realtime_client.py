import socketio
import threading


class RealtimeClient:

    def __init__(self, server_url="http://127.0.0.1:5000"):
        self.server_url = server_url
        self.sio = socketio.Client()

        # ================= STATE =================
        self.current_room = None

        self.participants = set()
        self.speakers = set()
        self.raised_hands = set()
        self.muted_users = set()

        # ================= CALLBACKS (UI HOOKS) =================
        self.on_update = None  # UI refresh hook

        # ================= EVENTS =================
        self._register_events()

        # Run in background thread
        self.thread = threading.Thread(target=self._connect, daemon=True)
        self.thread.start()

    # ================= CONNECT =================
    def _connect(self):
        try:
            self.sio.connect(self.server_url)
            print("🟢 Realtime connected")
        except Exception as e:
            print("❌ Realtime connection error:", e)

    # ================= ROOM JOIN =================
    def join_room(self, room_id):
        self.current_room = room_id
        self.sio.emit("join_room", {"room": room_id})
        print("📡 Joined realtime room:", room_id)

    def leave_room(self):
        if self.current_room:
            self.sio.emit("leave_room", {"room": self.current_room})
            self.current_room = None

    # ================= EVENT REGISTRATION =================
    def _register_events(self):

        @self.sio.on("connect")
        def on_connect():
            print("🔗 Socket connected")

        @self.sio.on("room_joined")
        def on_room_joined(data):
            print("🏠 Room joined:", data)

        # ================= PARTICIPANT UPDATE =================
        @self.sio.on("participant_update")
        def on_participant_update(data):
            self._sync_space(data)

        # ================= HAND RAISE =================
        @self.sio.on("hand_update")
        def on_hand_update(data):
            self._sync_space(data)

        # ================= MUTE EVENT =================
        @self.sio.on("mute_event")
        def on_mute_event(data):
            user = data.get("user")
            self.muted_users.add(user)
            print("🔇 Muted via host:", user)

        # ================= KICK EVENT =================
        @self.sio.on("kick_event")
        def on_kick_event(data):
            user = data.get("user")

            self.participants.discard(user)
            self.speakers.discard(user)
            self.raised_hands.discard(user)

            print("🚫 Kicked:", user)

        # ================= SPEAKER UPDATE =================
        @self.sio.on("speaker_update")
        def on_speaker_update(data):
            self._sync_space(data)

    # ================= SYNC FULL SPACE STATE =================
    def _sync_space(self, data):

        self.participants = set(data.get("participants", []))
        self.speakers = set(data.get("speakers", []))
        self.raised_hands = set(data.get("raised_hands", []))
        self.muted_users = set(data.get("muted_users", []))

        print("🔄 Space synced")

        # notify UI
        if self.on_update:
            self.on_update()

    # ================= HELPERS =================
    def get_participants(self):
        return list(self.participants)

    def get_speakers(self):
        return list(self.speakers)

    def get_raised_hands(self):
        return list(self.raised_hands)

    def is_muted(self, user):
        return user in self.muted_users

    # ================= CLEANUP =================
    def disconnect(self):
        try:
            self.sio.disconnect()
        except:
            pass
