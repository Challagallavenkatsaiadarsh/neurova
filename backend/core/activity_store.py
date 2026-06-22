# backend/core/activity_store.py

import os
import json
import copy

# =========================================================
# STORAGE FILE
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVITY_FILE = os.path.join(BASE_DIR, "activity_store.json")

DEFAULT_STORE = {
    "likes": {},
    "replies": {},
    "reposts": {},
    "shares": {},
    "bookmarks": {}
}


# =========================================================
# LOAD FROM DISK
# =========================================================
def load_store():
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict):
                    # ensure all keys exist
                    for k in DEFAULT_STORE:
                        data.setdefault(k, {})
                    return data

        except Exception as e:
            print("❌ Load error:", e)

    return copy.deepcopy(DEFAULT_STORE)


# =========================================================
# GLOBAL CACHE
# =========================================================
ACTIVITY_STORE = load_store()


# =========================================================
# FORCE SYNC
# =========================================================
def refresh_store():
    global ACTIVITY_STORE
    ACTIVITY_STORE = load_store()


# =========================================================
# ATOMIC SAVE (CRITICAL FOR PERSISTENCE)
# =========================================================
def save_store():
    try:
        tmp = ACTIVITY_FILE + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(ACTIVITY_STORE, f, indent=4, ensure_ascii=False)

        os.replace(tmp, ACTIVITY_FILE)

    except Exception as e:
        print("❌ Save error:", e)


# =========================================================
# ADD ACTIVITY (LIKES / REPLIES / REPOSTS / ETC)
# =========================================================
def add_activity(activity_type, user_id, post):

    refresh_store()

    if activity_type not in ACTIVITY_STORE:
        ACTIVITY_STORE[activity_type] = {}

    if user_id not in ACTIVITY_STORE[activity_type]:
        ACTIVITY_STORE[activity_type][user_id] = []

    if not isinstance(post, dict):
        return

    post_id = (
        post.get("post_id")
        or post.get("space_id")
        or post.get("room_id")
        or post.get("id")
    )

    if not post_id:
        return

    normalized_post = {
        "post_id": str(post_id),
        "username": post.get("username", "unknown"),
        "text": post.get("text", ""),
        "image": post.get("image", ""),
        "source": post.get("source") or post.get("type") or "feed",
        "space_id": str(
            post.get("space_id")
            or post.get("room_id")
            or post.get("id")
            or post_id
        )
    }

    existing = ACTIVITY_STORE[activity_type][user_id]

    # prevent duplicates
    if not any(p.get("post_id") == normalized_post["post_id"] for p in existing):
        existing.append(normalized_post)
        save_store()   # 🔥 SAVE EVERY TIME FOR ALL TYPES

        print(f"✅ STORED {activity_type} | user={user_id} | id={post_id}")
    else:
        print(f"ℹ️ EXISTS {activity_type} | id={post_id}")


# =========================================================
# REMOVE ACTIVITY (UNLIKE / UNBOOKMARK / etc)
# =========================================================
def remove_activity(activity_type, user_id, post_id):

    refresh_store()

    if activity_type not in ACTIVITY_STORE:
        return

    if user_id not in ACTIVITY_STORE[activity_type]:
        return

    ACTIVITY_STORE[activity_type][user_id] = [
        p for p in ACTIVITY_STORE[activity_type][user_id]
        if str(p.get("post_id")) != str(post_id)
    ]

    save_store()

    print(f"🗑 REMOVED {activity_type} | user={user_id} | id={post_id}")


# =========================================================
# GET ACTIVITY (ALWAYS FRESH FOR ALL TABS)
# =========================================================
def get_activity(activity_type, user_id):

    refresh_store()

    return ACTIVITY_STORE.get(activity_type, {}).get(user_id, [])


# =========================================================
# CLEAR ALL (OPTIONAL)
# =========================================================
def clear_activity(activity_type, user_id):

    refresh_store()

    if activity_type in ACTIVITY_STORE and user_id in ACTIVITY_STORE[activity_type]:
        ACTIVITY_STORE[activity_type][user_id] = []
        save_store()

    print(f"🧹 CLEARED {activity_type} | user={user_id}")
