# =========================================
# FILE: live_voice_session.py
# =========================================

import time


class LiveVoiceSession:

    def __init__(self):

        # room_id -> room state
        self.rooms = {}

    # =========================================
    # CREATE ROOM
    # =========================================
    def create_room(self, room_id, host):

        if room_id not in self.rooms:

            self.rooms[room_id] = {

                "host": host,
                "cohosts": set(),

                "speakers": set(),
                "muted": set(),

                "active_speaker": None,

                "raise_hand_queue": [],

                "last_activity": {},
                "speaking_state": {}
            }

    # =========================================
    # JOIN ROOM
    # =========================================
    def join(self, room_id, user):

        self.create_room(room_id, user)

        self.rooms[room_id]["last_activity"][user] = time.time()

    # =========================================
    # RAISE HAND
    # =========================================
    def raise_hand(self, room_id, user):

        room = self.rooms.get(room_id)
        if not room:
            return

        if user not in room["raise_hand_queue"]:
            room["raise_hand_queue"].append(user)

    # =========================================
    # APPROVE SPEAKER
    # =========================================
    def approve_speaker(self, room_id, user):

        room = self.rooms.get(room_id)
        if not room:
            return

        room["speakers"].add(user)

        if user in room["raise_hand_queue"]:
            room["raise_hand_queue"].remove(user)

    # =========================================
    # MUTE USER
    # =========================================
    def mute_speaker(self, room_id, user):

        room = self.rooms.get(room_id)
        if not room:
            return

        room["muted"].add(user)

        if room["active_speaker"] == user:
            room["active_speaker"] = None

    # =========================================
    # SPEAKING UPDATE
    # =========================================
    def update_speaking(self, room_id, user, is_speaking):

        room = self.rooms.get(room_id)
        if not room:
            return

        room["speaking_state"][user] = is_speaking
        room["last_activity"][user] = time.time()

        # ONLY ONE ACTIVE SPEAKER RULE
        if is_speaking and room["active_speaker"] is None:
            room["active_speaker"] = user

    # =========================================
    # GET STATE
    # =========================================
    def get_state(self, room_id):

        return self.rooms.get(room_id, {})

    # =========================================
    # CLEANUP GHOST USERS
    # =========================================
    def cleanup(self, timeout=60):

        now = time.time()

        for room_id, room in self.rooms.items():

            dead_users = []

            for user, last in room["last_activity"].items():

                if now - last > timeout:
                    dead_users.append(user)

            for user in dead_users:

                room["speakers"].discard(user)
                room["muted"].discard(user)

                if room["active_speaker"] == user:
                    room["active_speaker"] = None

                room["last_activity"].pop(user, None)
                room["speaking_state"].pop(user, None)

            # FIX invalid active speaker
            if room["active_speaker"] not in room["speakers"]:
                room["active_speaker"] = None
