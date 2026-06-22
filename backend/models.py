# =========================
# DATABASE MODELS (POSTGRES READY - CLUBHOUSE SYSTEM)
# =========================

from datetime import datetime
from db import Database


# ==========================================================
# 🟣 SPACE MODEL (LOGIC + CACHE LAYER)
# ==========================================================
class Space:
    def __init__(self, space_id, name, topic, host):
        self.space_id = space_id
        self.name = name
        self.topic = topic
        self.host = host
        self.created_at = datetime.utcnow()

        # =========================
        # LIVE STATE (IN-MEMORY CACHE)
        # =========================
        self.participants = []
        self.speakers = []
        self.cohosts = []
        self.raised_hands = []
        self.muted_users = []
        self.kicked_users = []
        self.speak_requests = []

        # 🔴 LIVE SPEAKING STATE
        self.active_speaker = None

        # 🔊 PUSH-TO-TALK / AUDIO STATE TRACKING (OPTIONAL EXTENSION)
        self.speaking_users = set()

    # =========================
    # SERIALIZE FOR SOCKET + API
    # =========================
    def to_dict(self):
        return {
            "space_id": self.space_id,
            "name": self.name,
            "topic": self.topic,
            "host": self.host,
            "created_at": self.created_at.isoformat(),

            # LIVE STATE
            "participants": self.participants,
            "speakers": self.speakers,
            "cohosts": self.cohosts,
            "raised_hands": self.raised_hands,
            "muted_users": self.muted_users,
            "kicked_users": self.kicked_users,
            "speak_requests": self.speak_requests,

            # REAL-TIME AUDIO STATE
            "active_speaker": self.active_speaker,
            "speaking_users": list(self.speaking_users)
        }


# ==========================================================
# 👤 USER MODEL
# ==========================================================
class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at.isoformat()
        }


# ==========================================================
# 🟢 POSTGRES TABLES (CLUBHOUSE CORE SCHEMA)
# ==========================================================

# =========================
# SPACES TABLE (PERSISTENCE LAYER)
# =========================
CREATE_SPACES_TABLE = """
CREATE TABLE IF NOT EXISTS spaces (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    topic TEXT,
    host TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    -- REALTIME SNAPSHOT (optional persistence fields)
    participants JSONB DEFAULT '[]',
    speakers JSONB DEFAULT '[]',
    cohosts JSONB DEFAULT '[]',
    raised_hands JSONB DEFAULT '[]',
    muted_users JSONB DEFAULT '[]',
    kicked_users JSONB DEFAULT '[]',
    speak_requests JSONB DEFAULT '[]',
    active_speaker TEXT
);
"""

# =========================
# USERS TABLE
# =========================
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# =========================
# SPEAK REQUESTS TABLE
# =========================
CREATE_SPEAK_REQUESTS_TABLE = """
CREATE TABLE IF NOT EXISTS speak_requests (
    id SERIAL PRIMARY KEY,
    space_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# =========================
# VOICE EVENTS TABLE (REAL-TIME TRACKING)
# =========================
CREATE_VOICE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS voice_events (
    id SERIAL PRIMARY KEY,
    space_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,   -- join, leave, mute, speaking_start, speaking_stop
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# =========================
# COHOSTS TABLE (RELATION TABLE)
# =========================
CREATE_COHOSTS_TABLE = """
CREATE TABLE IF NOT EXISTS cohosts (
    id SERIAL PRIMARY KEY,
    space_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""


# ==========================================================
# 🧠 DATABASE INITIALIZATION
# ==========================================================
async def init_db():
    """
    Initialize PostgreSQL schema for full Clubhouse system.
    """

    await Database.execute(CREATE_SPACES_TABLE)
    await Database.execute(CREATE_USERS_TABLE)
    await Database.execute(CREATE_SPEAK_REQUESTS_TABLE)
    await Database.execute(CREATE_VOICE_EVENTS_TABLE)
    await Database.execute(CREATE_COHOSTS_TABLE)

    print("✅ PostgreSQL schema initialized (Full realtime + persistence ready)")


# ==========================================================
# ⚡ IMPORTANT DB USAGE PATTERN
# ==========================================================
"""
Correct usage (IMPORTANT FIX YOU ALREADY STARTED USING):

await Database.execute(
    "INSERT INTO speak_requests(space_id, user_id) VALUES (%s, %s)",
    room, user
)

await Database.fetch_all(
    "SELECT * FROM speak_requests WHERE space_id=%s",
    room
)

REAL USAGE IDEA (LIVE SYNC + PERSISTENCE):

1. On space create:
   -> INSERT INTO spaces

2. On join:
   -> UPDATE spaces participants JSONB

3. On speak request:
   -> INSERT INTO speak_requests

4. On speaking event:
   -> UPDATE spaces SET active_speaker

5. On cleanup:
   -> DELETE FROM spaces WHERE last_active < NOW() - INTERVAL '2 hours'
"""
