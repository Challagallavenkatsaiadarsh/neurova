import json
import os

from backend.ai.live_spaces_engine import LiveSpacesEngine


# =========================================
# SAFE PATH
# =========================================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

SPACES_FILE = os.path.join(BASE_DIR, "ai", "spaces.json")


class SpacesStore:

    def __init__(self):

        os.makedirs(os.path.dirname(SPACES_FILE), exist_ok=True)

        # 🔥 LIVE ENGINE CONNECT
        self.live = LiveSpacesEngine()

        # 🔥 AUTO CREATE IF MISSING OR CORRUPT
        if not os.path.exists(SPACES_FILE):
            self._init()
        else:
            try:
                self.load()
            except Exception:
                self._init()

    # =========================================
    # INIT FILE (LEGACY + X-SPACES READY)
    # =========================================
    def _init(self):

        data = {
            "spaces": {
                "ipl_live": {
                    "name": "IPL LIVE FAN SPACE",
                    "host": "NeuroAdmin",
                    "users": [],
                    "messages": []
                },
                "movie_talk": {
                    "name": "MOVIE CELEBRITY TALK",
                    "host": "CinemaBot",
                    "users": [],
                    "messages": []
                },
                "ai_future": {
                    "name": "AI FUTURE DISCUSSION",
                    "host": "NeuroAI",
                    "users": [],
                    "messages": []
                },
                "anime_space": {
                    "name": "ANIME COMMUNITY SPACE",
                    "host": "AnimeHub",
                    "users": [],
                    "messages": []
                }
            }
        }

        self._write(data)

    # =========================================
    # JOIN SPACE (LIVE SYNC + X STYLE)
    # =========================================
    def join_space(self, space_id, user_id):

        data = self.load()

        space = data["spaces"].get(space_id)
        if not space:
            return False

        if user_id not in space["users"]:
            space["users"].append(user_id)

        # 🔥 LIVE ENGINE SYNC
        self.live.create_space(space_id, space["host"])
        self.live.join(space_id, user_id)

        self._write(data)
        return True

    # =========================================
    # LEAVE SPACE
    # =========================================
    def leave_space(self, space_id, user_id):

        data = self.load()

        space = data["spaces"].get(space_id)
        if not space:
            return False

        if user_id in space["users"]:
            space["users"].remove(user_id)

        # 🔥 LIVE ENGINE SYNC
        self.live.leave(space_id, user_id)

        self._write(data)
        return True

    # =========================================
    # SEND MESSAGE (LIVE CHAT)
    # =========================================
    def send_message(self, space_id, user_id, message):

        data = self.load()

        space = data["spaces"].get(space_id)
        if not space:
            return False

        msg = {
            "user": user_id,
            "text": message
        }

        space["messages"].append(msg)
        space["messages"] = space["messages"][-50:]

        # 🔥 LIVE ENGINE SYNC
        self.live.send_message(space_id, user_id, message)

        self._write(data)
        return True

    # =========================================
    # GET SPACE (WITH LIVE MERGE)
    # =========================================
    def get_space(self, space_id):

        data = self.load()
        space = data["spaces"].get(space_id)

        if not space:
            return None

        # 🔥 MERGE LIVE DATA (X STYLE REAL-TIME VIEW)
        live_data = self.live.get_live_data(space_id)

        if live_data:
            space = dict(space)  # avoid mutation
            space["live"] = live_data

        return space

    # =========================================
    # GET ALL SPACES
    # =========================================
    def get_all_spaces(self):

        data = self.load()
        return data.get("spaces", {})

    # =========================================
    # SAFE LOAD
    # =========================================
    def load(self):

        if not os.path.exists(SPACES_FILE):
            return {"spaces": {}}

        try:
            with open(SPACES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    return {"spaces": {}}

                return json.loads(content)

        except json.JSONDecodeError:
            self._init()
            return {"spaces": {}}

        except Exception:
            return {"spaces": {}}

    # =========================================
    # SAFE WRITE
    # =========================================
    def _write(self, data):

        with open(SPACES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
