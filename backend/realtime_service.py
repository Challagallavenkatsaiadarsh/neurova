import threading
import time
from backend.firebase_client import db
from google.cloud import firestore

POSTS_COLLECTION = "posts"


class RealtimeService:
    """
    Firebase-based REAL-TIME feed sync (polling system)
    Safe for Kivy apps (Android + Desktop)
    """

    def __init__(self, callback, interval=2):
        """
        callback → function(posts_list)
        interval → polling speed (seconds)
        """
        self.callback = callback
        self.interval = interval

        self.running = False
        self.thread = None

        # store last known state (for change detection)
        self.last_snapshot = {}

        # anti-spam update control
        self.last_push_time = 0
        self.min_push_gap = 1  # seconds

    # ================= START SERVICE =================
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    # ================= STOP SERVICE =================
    def stop(self):
        self.running = False

    # ================= CORE LOOP =================
    def _run(self):
        while self.running:
            try:
                posts_ref = db.collection(POSTS_COLLECTION).stream()

                updated_snapshot = {}
                posts_list = []

                for doc in posts_ref:
                    post = doc.to_dict()
                    post["id"] = doc.id

                    # normalize missing fields (important for stability)
                    post.setdefault("likes", [])
                    post.setdefault("comments", [])
                    post.setdefault("image", "")
                    post.setdefault("username", "user")

                    updated_snapshot[doc.id] = post
                    posts_list.append(post)

                # sort newest first
                def sort_key(x):
                    ts = x.get("createdAt")
                    if hasattr(ts, "timestamp"):
                        return ts.timestamp()
                    return 0

                posts_list.sort(key=sort_key, reverse=True)

                # detect changes
                if self._has_changes(updated_snapshot):
                    self.last_snapshot = updated_snapshot

                    # throttle UI updates (prevents flicker)
                    now = time.time()
                    if now - self.last_push_time > self.min_push_gap:
                        self.last_push_time = now
                        self.callback(posts_list)

            except Exception as e:
                print("RealtimeService error:", e)

            time.sleep(self.interval)

    # ================= CHANGE DETECTION =================
    def _has_changes(self, new_snapshot):
        """
        Detect changes safely (likes/comments/posts)
        """
        if len(new_snapshot) != len(self.last_snapshot):
            return True

        for post_id, post in new_snapshot.items():
            old_post = self.last_snapshot.get(post_id)

            if not old_post:
                return True

            # compare important fields only (faster)
            if (
                post.get("likes") != old_post.get("likes")
                or post.get("comments") != old_post.get("comments")
                or post.get("text") != old_post.get("text")
                or post.get("image") != old_post.get("image")
            ):
                return True

        return False
