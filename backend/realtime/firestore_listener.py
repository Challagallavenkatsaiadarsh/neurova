import threading

from backend.firebase_client import db

POSTS_COLLECTION = "posts"


class FirestoreRealtimeListener:
    """
    TRUE Firestore real-time listener
    """

    def __init__(self, callback):
        self.callback = callback
        self.listener = None
        self.running = False

    # ================= START =================
    def start(self):

        if self.running:
            return

        self.running = True

        col_ref = db.collection(POSTS_COLLECTION)

        self.listener = col_ref.on_snapshot(
            self._on_snapshot
        )

    # ================= STOP =================
    def stop(self):

        self.running = False

        if self.listener:
            self.listener.unsubscribe()

    # ================= SNAPSHOT =================
    def _on_snapshot(self, docs, changes, read_time):

        try:
            posts = []

            for doc in docs:

                post = doc.to_dict()

                post["id"] = doc.id

                post["comments"] = post.get("comments", [])
                post["likes"] = post.get("likes", [])
                post["bookmarks"] = post.get("bookmarks", [])
                post["reposts"] = post.get("reposts", [])
                post["shares"] = post.get("shares", 0)

                posts.append(post)

            def sort_key(x):
                ts = x.get("createdAt")

                if hasattr(ts, "timestamp"):
                    return ts.timestamp()

                return 0

            posts = sorted(
                posts,
                key=sort_key,
                reverse=True
            )

            self.callback(posts)

        except Exception as e:
            print("Firestore realtime error:", e)
