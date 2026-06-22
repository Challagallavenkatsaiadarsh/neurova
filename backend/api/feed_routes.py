from flask import Blueprint, jsonify, request
from backend.firebase_client import db
from google.cloud import firestore
import uuid
from datetime import datetime

feed_bp = Blueprint("feed", __name__)

POSTS_COLLECTION = "posts"

# =========================================================
# 🌍 FEED ROUTES (NO /api PREFIX)
# =========================================================

@feed_bp.route("/", methods=["GET"])
def get_feed():
    try:
        posts_ref = db.collection(POSTS_COLLECTION).stream()
        posts = []

        for doc in posts_ref:
            post = doc.to_dict()
            post["id"] = doc.id

            comments = post.get("comments", [])
            total_replies = len(comments) + sum(len(c.get("replies", [])) for c in comments)
            post["total_reply_count"] = total_replies

            post["username"] = post.get("Username", post.get("username", "user"))

            post.setdefault("likes", [])
            post.setdefault("comments", [])
            post.setdefault("bookmarks", [])
            post.setdefault("reposts", [])
            post.setdefault("shares", 0)
            post.setdefault("is_pinned", False)

            posts.append(post)

        def sort_key(x):
            if x.get("is_pinned"):
                return float("inf")
            ts = x.get("createdAt")
            return ts.timestamp() if hasattr(ts, "timestamp") else 0

        posts.sort(key=sort_key, reverse=True)

        return jsonify({"posts": posts})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# CREATE POST
# =========================================================
@feed_bp.route("/create", methods=["POST"])
def create_post():
    try:
        data = request.json

        post = {
            "username": data.get("username", "user"),
            "text": data.get("text", ""),
            "image": data.get("image", ""),
            "likes": [],
            "comments": [],
            "bookmarks": [],
            "reposts": [],
            "shares": 0,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "is_pinned": False,
            "quoted_post": data.get("quoted_post", None)
        }

        doc_ref = db.collection(POSTS_COLLECTION).add(post)

        return jsonify({
            "message": "Post created successfully",
            "post_id": doc_ref[1].id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# EDIT POST
# =========================================================
@feed_bp.route("/edit/<post_id>", methods=["PUT"])
def edit_post(post_id):
    try:
        data = request.json
        ref = db.collection(POSTS_COLLECTION).document(post_id)

        if not ref.get().exists:
            return jsonify({"error": "Post not found"}), 404

        update_data = {}
        if "text" in data:
            update_data["text"] = data["text"]
        if "image" in data:
            update_data["image"] = data["image"]

        ref.update(update_data)

        return jsonify({"message": "Post updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# DELETE POST
# =========================================================
@feed_bp.route("/delete/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        ref = db.collection(POSTS_COLLECTION).document(post_id)

        if not ref.get().exists:
            return jsonify({"error": "Post not found"}), 404

        ref.delete()

        return jsonify({"message": "Post deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# PIN / UNPIN
# =========================================================
@feed_bp.route("/pin/<post_id>", methods=["POST"])
def pin_post(post_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)
    if not ref.get().exists:
        return jsonify({"error": "Post not found"}), 404

    ref.update({"is_pinned": True})
    return jsonify({"message": "Post pinned"})


@feed_bp.route("/unpin/<post_id>", methods=["POST"])
def unpin_post(post_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)
    if not ref.get().exists:
        return jsonify({"error": "Post not found"}), 404

    ref.update({"is_pinned": False})
    return jsonify({"message": "Post unpinned"})


# =========================================================
# 🔥 TOGGLE SYSTEM (LIKES / BOOKMARKS / REPOSTS)
# =========================================================
def toggle_array(ref, field, user="user"):
    data = ref.get().to_dict()
    arr = data.get(field, [])

    if user in arr:
        ref.update({field: firestore.ArrayRemove([user])})
        return False
    else:
        ref.update({field: firestore.ArrayUnion([user])})
        return True


@feed_bp.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)

    if not ref.get().exists:
        return jsonify({"error": "Post not found"}), 404

    liked = toggle_array(ref, "likes")

    return jsonify({
        "liked": liked,
        "likes_count": len(ref.get().to_dict().get("likes", []))
    })


@feed_bp.route("/bookmark/<post_id>", methods=["POST"])
def bookmark(post_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)

    if not ref.get().exists:
        return jsonify({"error": "Post not found"}), 404

    bookmarked = toggle_array(ref, "bookmarks")

    return jsonify({"bookmarked": bookmarked})


@feed_bp.route("/repost/<post_id>", methods=["POST"])
def repost(post_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)

    if not ref.get().exists:
        return jsonify({"error": "Post not found"}), 404

    reposted = toggle_array(ref, "reposts")

    return jsonify({"reposted": reposted})


# =========================================================
# 💬 COMMENT SYSTEM
# =========================================================
@feed_bp.route("/comment/<post_id>", methods=["POST"])
def add_comment(post_id):
    try:
        data = request.json
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Comment cannot be empty"}), 400

        ref = db.collection(POSTS_COLLECTION).document(post_id)

        if not ref.get().exists:
            return jsonify({"error": "Post not found"}), 404

        comment = {
            "id": str(uuid.uuid4()),
            "username": data.get("username", "user"),
            "text": text,
            "createdAt": datetime.utcnow().isoformat(),
            "likes": [],
            "bookmarks": [],
            "reposts": [],
            "shares": 0,
            "replies": [],
            "quoted_post": data.get("quoted_post")
        }

        post_data = ref.get().to_dict()
        comments = post_data.get("comments", [])
        comments.append(comment)

        ref.update({"comments": comments})

        return jsonify({
            "message": "Comment added",
            "comment": comment,
            "comments_count": len(comments)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# REPLY COMMENT
# =========================================================
@feed_bp.route("/comment/reply/<post_id>/<comment_id>", methods=["POST"])
def reply_comment(post_id, comment_id):
    try:
        data = request.json
        ref = db.collection(POSTS_COLLECTION).document(post_id)

        if not ref.get().exists:
            return jsonify({"error": "Post not found"}), 404

        post = ref.get().to_dict()
        comments = post.get("comments", [])

        for comment in comments:
            if comment["id"] == comment_id:
                comment.setdefault("replies", [])

                reply = {
                    "id": str(uuid.uuid4()),
                    "username": data.get("username", "user"),
                    "text": data.get("text", ""),
                    "createdAt": datetime.utcnow().isoformat()
                }

                comment["replies"].append(reply)
                break

        ref.update({"comments": comments})

        return jsonify({"message": "Reply added"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# COMMENT TOGGLE SYSTEM
# =========================================================
def toggle_comment(post_id, comment_id, field):
    ref = db.collection(POSTS_COLLECTION).document(post_id)
    post = ref.get().to_dict()
    comments = post.get("comments", [])

    for c in comments:
        if c["id"] == comment_id:
            c.setdefault(field, [])

            if field == "shares":
                c[field] = c.get(field, 0) + 1
            else:
                user = "user"
                if user in c[field]:
                    c[field].remove(user)
                else:
                    c[field].append(user)

    ref.update({"comments": comments})


@feed_bp.route("/comment/like/<post_id>/<comment_id>", methods=["POST"])
def like_comment(post_id, comment_id):
    toggle_comment(post_id, comment_id, "likes")
    return jsonify({"message": "comment liked", "success": True})


@feed_bp.route("/comment/bookmark/<post_id>/<comment_id>", methods=["POST"])
def bookmark_comment(post_id, comment_id):
    toggle_comment(post_id, comment_id, "bookmarks")
    return jsonify({"message": "comment bookmarked", "success": True})


@feed_bp.route("/comment/repost/<post_id>/<comment_id>", methods=["POST"])
def repost_comment(post_id, comment_id):
    toggle_comment(post_id, comment_id, "reposts")
    return jsonify({"message": "comment reposted", "success": True})


@feed_bp.route("/comment/share/<post_id>/<comment_id>", methods=["POST"])
def share_comment(post_id, comment_id):
    toggle_comment(post_id, comment_id, "shares")
    return jsonify({"message": "comment shared", "success": True})


# =========================================================
# COMMENT EDIT / DELETE
# =========================================================
@feed_bp.route("/comment/edit/<post_id>/<comment_id>", methods=["PUT"])
def edit_comment(post_id, comment_id):
    data = request.json
    ref = db.collection(POSTS_COLLECTION).document(post_id)
    post = ref.get().to_dict()

    comments = post.get("comments", [])

    for c in comments:
        if c["id"] == comment_id:
            c["text"] = data.get("text", c["text"])

    ref.update({"comments": comments})

    return jsonify({"message": "Comment updated"})


@feed_bp.route("/comment/delete/<post_id>/<comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    ref = db.collection(POSTS_COLLECTION).document(post_id)
    comments = ref.get().to_dict().get("comments", [])

    new_comments = [c for c in comments if c["id"] != comment_id]

    ref.update({"comments": new_comments})

    return jsonify({"message": "Comment deleted"})
