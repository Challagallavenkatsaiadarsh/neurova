# =========================================
# NEUROVA MEMORY SYSTEM (LEVEL 5+ STABLE + NOTIFICATIONS + HASHTAGS)
# =========================================

import json
import os
import re
from collections import Counter

# =========================================
# SAFE PATH SETUP
# =========================================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MEMORY_FILE = os.path.join(BASE_DIR, "ai", "memory.json")


class MemoryStore:

    def __init__(self):

        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

        if not os.path.exists(MEMORY_FILE):
            self._init_file()
        else:
            try:
                self.load_all()
            except Exception:
                self._init_file()

    # =========================================
    # INIT FILE
    # =========================================
    def _init_file(self):

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "users": {},
                    "notifications": []
                },
                f,
                indent=2
            )

    # =========================================
    # HASHTAGS
    # =========================================
    def extract_hashtags(self, message: str):
        return re.findall(r"#(\w+)", message.lower())

    # =========================================
    # SAVE USER POST + NOTIFICATION
    # =========================================
    def save(self, user_id, message, verified=False):

        data = self.load_all()

        # ensure structure
        data.setdefault("users", {})
        data.setdefault("notifications", [])

        # user posts
        data["users"].setdefault(user_id, [])

        hashtags = self.extract_hashtags(message)

        post = {
            "text": message,
            "hashtags": hashtags,
            "verified": verified
        }

        data["users"][user_id].append(post)

        # keep last 20 posts
        data["users"][user_id] = data["users"][user_id][-20:]

        # create notification entry
        self.add_notification(user_id, message, verified)

        self._write(data)

    # =========================================
    # NOTIFICATIONS SYSTEM
    # =========================================
    def add_notification(self, user_id, message, verified=False):

        data = self.load_all()

        data.setdefault("notifications", [])

        data["notifications"].append({
            "user": user_id,
            "text": message,
            "verified": verified
        })

        # keep last 50 notifications
        data["notifications"] = data["notifications"][-50:]

        self._write(data)

    # =========================================
    # GET NOTIFICATIONS (FOR SCREEN)
    # =========================================
    def get_notifications(self, mode="all"):

        data = self.load_all()
        notifications = data.get("notifications", [])

        if mode == "verified":
            return [
                n for n in notifications
                if n.get("verified") is True
            ]

        return notifications

    # =========================================
    # EMPTY STATE SUPPORT (IMPORTANT FOR UI)
    # =========================================
    def has_notifications(self):

        data = self.load_all()
        return len(data.get("notifications", [])) > 0

    # =========================================
    # GET USER MEMORY
    # =========================================
    def get(self, user_id):

        data = self.load_all()
        return data.get("users", {}).get(user_id, [])

    # =========================================
    # HASHTAG SEARCH
    # =========================================
    def search_by_hashtag(self, tag):

        tag = tag.lower().replace("#", "")

        data = self.load_all()
        results = []

        for user, messages in data.get("users", {}).items():
            for msg in messages:
                if tag in msg.get("hashtags", []):
                    results.append({
                        "user": user,
                        "text": msg["text"],
                        "hashtags": msg.get("hashtags", [])
                    })

        return results

    # =========================================
    # TRENDING HASHTAGS
    # =========================================
    def get_trending(self, limit=10):

        data = self.load_all()

        all_tags = []

        for messages in data.get("users", {}).values():
            for msg in messages:
                all_tags.extend(msg.get("hashtags", []))

        counter = Counter(all_tags)

        return counter.most_common(limit)

    # =========================================
    # SAFE LOAD
    # =========================================
    def load_all(self):

        if not os.path.exists(MEMORY_FILE):
            return {}

        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    return {}

                return json.loads(content)

        except json.JSONDecodeError:
            self._init_file()
            return {}

        except Exception:
            return {}

    # =========================================
    # SAFE WRITE
    # =========================================
    def _write(self, data):

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
