# ==============================
# FILE: live_spaces_engine.py
# ==============================

import threading
import time
from collections import defaultdict


class LiveSpacesEngine:

    def __init__(self):

        self.users = defaultdict(set)

        # 🎤 SPEAKERS / ROLES
        self.speakers = defaultdict(set)
        self.cohosts = defaultdict(set)

        # ✋ REQUEST SYSTEM
        self.raise_hand_queue = defaultdict(list)
        self.cohost_invites = defaultdict(dict)

        # 🔇 MUTED USERS
        self.muted_users = defaultdict(set)

        # 🎧 ACTIVE TALK STATE
        self.active_talkers = defaultdict(set)

        # 💬 CHAT / REACTIONS / AUDIO
        self.messages = defaultdict(list)
        self.reactions = defaultdict(list)
        self.audio_streams = defaultdict(list)

        # ⚡ LAST EVENT PIPELINE (FOR FAST BROADCAST SYNC)
        self._last_event = None

        # 🔒 THREAD SAFETY
        self.lock = threading.Lock()

        # 🧠 USER ACTIVITY TRACKING (🔥 FIX FOR GHOST USERS)
        self.last_seen = defaultdict(dict)   # space_id -> {user: timestamp}
        self.speaking_state = defaultdict(dict)  # space_id -> {user: bool}

        print("🟣 LIVE SPACES ENGINE (LIVEKIT READY + CLEAN STATE + NO GHOSTS)")

    # =========================================
    # SPACE INIT
    # =========================================
    def create_space(self, space_id, host):

        with self.lock:
            self.users[space_id].add(host)
            self.speakers[space_id].add(host)

            self.last_seen[space_id][host] = time.time()
            self.speaking_state[space_id][host] = False

    # =========================================
    # JOIN SPACE
    # =========================================
    def join(self, space_id, user_id):

        with self.lock:
            self.users[space_id].add(user_id)
            self.last_seen[space_id][user_id] = time.time()
            self.speaking_state[space_id][user_id] = False

        self.broadcast(space_id, {
            "type": "join",
            "user": user_id
        })

    # =========================================
    # LEAVE SPACE (FULL CLEANUP FIX)
    # =========================================
    def leave(self, space_id, user_id):

        with self.lock:

            self.users[space_id].discard(user_id)
            self.speakers[space_id].discard(user_id)
            self.cohosts[space_id].discard(user_id)
            self.active_talkers[space_id].discard(user_id)
            self.muted_users[space_id].discard(user_id)

            self.last_seen[space_id].pop(user_id, None)
            self.speaking_state[space_id].pop(user_id, None)

            if user_id in self.raise_hand_queue[space_id]:
                self.raise_hand_queue[space_id].remove(user_id)

            self.cohost_invites[space_id].pop(user_id, None)

        self.broadcast(space_id, {
            "type": "leave",
            "user": user_id
        })

    # =========================================
    # REQUEST SPEAK
    # =========================================
    def request_speak(self, space_id, user_id):

        if user_id not in self.raise_hand_queue[space_id]:
            self.raise_hand_queue[space_id].append(user_id)

        self.broadcast(space_id, {
            "type": "raise_hand",
            "user": user_id
        })

    # =========================================
    # APPROVE SPEAKER
    # =========================================
    def approve_speaker(self, space_id, host_id, user_id):

        self.speakers[space_id].add(user_id)

        if user_id in self.raise_hand_queue[space_id]:
            self.raise_hand_queue[space_id].remove(user_id)

        self.broadcast(space_id, {
            "type": "speaker_approved",
            "user": user_id
        })

    # =========================================
    # COHOST INVITE
    # =========================================
    def invite_cohost(self, space_id, host_id, target_user):

        self.cohost_invites[space_id][target_user] = True

        self.broadcast(space_id, {
            "type": "cohost_invite",
            "from": host_id,
            "user": target_user
        })

    # =========================================
    # ACCEPT COHOST
    # =========================================
    def accept_cohost(self, space_id, user_id):

        if not self.cohost_invites[space_id].get(user_id):
            return False

        self.cohosts[space_id].add(user_id)
        self.speakers[space_id].add(user_id)

        self.cohost_invites[space_id].pop(user_id, None)

        self.broadcast(space_id, {
            "type": "cohost_joined",
            "user": user_id
        })

        return True

    # =========================================
    # REMOVE COHOST
    # =========================================
    def remove_cohost(self, space_id, user_id):

        self.cohosts[space_id].discard(user_id)

        self.broadcast(space_id, {
            "type": "cohost_removed",
            "user": user_id
        })

    # =========================================
    # TALK STATE (SYNC WITH LIVEKIT)
    # =========================================
    def toggle_talk(self, space_id, user_id, is_talking):

        if user_id not in self.speakers[space_id]:
            return

        if user_id in self.muted_users[space_id]:
            return

        self.speaking_state[space_id][user_id] = is_talking

        if is_talking:
            self.active_talkers[space_id].add(user_id)
        else:
            self.active_talkers[space_id].discard(user_id)

        self.broadcast(space_id, {
            "type": "talk_state",
            "user": user_id,
            "active": is_talking
        })

    # =========================================
    # MUTE / UNMUTE
    # =========================================
    def mute_user(self, space_id, host_id, user_id):

        self.muted_users[space_id].add(user_id)
        self.active_talkers[space_id].discard(user_id)

        self.broadcast(space_id, {
            "type": "muted",
            "user": user_id
        })

    def unmute_user(self, space_id, host_id, user_id):

        self.muted_users[space_id].discard(user_id)

        self.broadcast(space_id, {
            "type": "unmuted",
            "user": user_id
        })

    # =========================================
    # CHAT
    # =========================================
    def send_message(self, space_id, user_id, message):

        msg = {"user": user_id, "text": message}

        self.messages[space_id].append(msg)
        self.messages[space_id] = self.messages[space_id][-50:]

        self.broadcast(space_id, {"type": "message", **msg})

    # =========================================
    # AUDIO
    # =========================================
    def send_audio(self, space_id, user_id, audio_data):

        if user_id in self.muted_users[space_id]:
            return False

        if user_id not in self.speakers[space_id]:
            return False

        self.last_seen[space_id][user_id] = time.time()

        event = {
            "type": "audio_chunk",
            "user": user_id,
            "data": audio_data
        }

        self.audio_streams[space_id].append(event)
        self.audio_streams[space_id] = self.audio_streams[space_id][-50:]

        self.broadcast(space_id, event)

        return True

    # =========================================
    # REACTIONS
    # =========================================
    def react(self, space_id, user_id, reaction):

        event = {
            "type": "reaction",
            "user": user_id,
            "reaction": reaction
        }

        self.reactions[space_id].append(event)
        self.reactions[space_id] = self.reactions[space_id][-100:]

        self.broadcast(space_id, event)

    # =========================================
    # BROADCAST PIPELINE
    # =========================================
    def broadcast(self, space_id, event):

        self._last_event = {
            "space_id": space_id,
            "event": event
        }

    # =========================================
    # LAST EVENT
    # =========================================
    def get_last_event(self):
        return self._last_event

    # =========================================
    # CLEAN GHOST USERS (🔥 IMPORTANT FIX)
    # =========================================
    def cleanup_inactive_users(self, timeout=60):

        now = time.time()
        to_remove = []

        for space_id, users in self.last_seen.items():

            for user_id, last in list(users.items()):

                if now - last > timeout:
                    to_remove.append((space_id, user_id))

        for space_id, user_id in to_remove:
            self.leave(space_id, user_id)

        if to_remove:
            print(f"🧹 Cleaned inactive users: {to_remove}")

    # =========================================
    # SNAPSHOT
    # =========================================
    def get_live_data(self, space_id):

        return {
            "users": list(self.users[space_id]),
            "speakers": list(self.speakers[space_id]),
            "cohosts": list(self.cohosts[space_id]),
            "queue": self.raise_hand_queue[space_id],
            "talking": list(self.active_talkers[space_id]),
            "muted": list(self.muted_users[space_id]),
            "messages": self.messages[space_id][-50:],
            "reactions": self.reactions[space_id][-50:],
            "audio": self.audio_streams[space_id][-50:]
        }
