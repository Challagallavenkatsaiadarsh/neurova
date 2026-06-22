from flask import Blueprint, request, jsonify
from firebase_client import db
from datetime import datetime, timezone

search_bp = Blueprint("search", __name__)


# =========================================
# SEARCH POSTS + USERS + HASHTAGS
# =========================================
@search_bp.route("/", methods=["GET"])
def search():
    try:
        query = request.args.get("q", "").strip().lower()

        if not query:
            return jsonify({
                "users": [],
                "posts": [],
                "hashtags": []
            })

        users_result = []
        posts_result = []
        hashtags_result = []

        # ================= USERS SEARCH =================
        users_ref = db.collection("users").stream()

        for doc in users_ref:
            user = doc.to_dict()

            username = user.get("username", "").lower()
            bio = user.get("bio", "").lower()

            if query in username or query in bio:
                users_result.append({
                    "id": doc.id,
                    "username": user.get("username", "user"),
                    "bio": user.get("bio", ""),
                    "profilePic": user.get("profilePic", "")
                })

        # ================= POSTS SEARCH =================
        posts_ref = db.collection("posts").stream()

        for doc in posts_ref:
            post = doc.to_dict()

            text = post.get("text", "").lower()

            if query in text:
                posts_result.append({
                    "id": doc.id,
                    "username": post.get("username", "user"),
                    "text": post.get("text", ""),
                    "image": post.get("image", ""),
                    "likes": post.get("likes", []),
                    "comments": post.get("comments", []),
                    "reposts": post.get("reposts", []),
                    "shares": post.get("shares", 0)
                })

        # ================= HASHTAGS SEARCH =================
        if query.startswith("#"):
            for post in posts_result:
                words = post.get("text", "").lower().split()

                for word in words:
                    if word.startswith("#") and word == query:
                        if word not in hashtags_result:
                            hashtags_result.append(word)

        return jsonify({
            "query": query,
            "users": users_result,
            "posts": posts_result,
            "hashtags": hashtags_result,
            "counts": {
                "users": len(users_result),
                "posts": len(posts_result),
                "hashtags": len(hashtags_result)
            }
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# TRENDING POSTS + TRENDING HASHTAGS
# =========================================
@search_bp.route("/trending", methods=["GET"])
def trending():
    try:

        posts_ref = db.collection("posts").stream()

        posts_with_score = []
        hashtag_counter = {}

        now = datetime.now(timezone.utc)

        for doc in posts_ref:

            post = doc.to_dict()
            post["id"] = doc.id

            text = post.get("text", "")

            # ================= HASHTAG COUNT =================
            for word in text.split():

                if word.startswith("#"):
                    tag = word.lower().strip()

                    hashtag_counter[tag] = (
                        hashtag_counter.get(tag, 0) + 1
                    )

            # ================= ENGAGEMENT =================
            likes = len(post.get("likes", []))
            comments = len(post.get("comments", []))
            reposts = len(post.get("reposts", []))
            shares = int(post.get("shares", 0))

            engagement = (
                likes +
                (comments * 2) +
                (reposts * 3) +
                (shares * 4)
            )

            # ================= AGE CALCULATION =================
            age_hours = 24

            created_at = post.get("createdAt")

            try:

                if created_at:

                    if isinstance(created_at, datetime):

                        age_hours = max(
                            (now - created_at).total_seconds() / 3600,
                            1
                        )

                    elif isinstance(created_at, str):

                        dt = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )

                        age_hours = max(
                            (now - dt).total_seconds() / 3600,
                            1
                        )

            except Exception:
                age_hours = 24

            # ================= TREND SCORE =================
            trend_score = engagement / (age_hours + 2)

            post["trend_score"] = round(
                trend_score,
                2
            )

            posts_with_score.append(post)

        # ================= SORT POSTS =================
        posts_with_score.sort(
            key=lambda p: p.get("trend_score", 0),
            reverse=True
        )

        # ================= SORT HASHTAGS =================
        trending_tags = sorted(
            hashtag_counter.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

        return jsonify({
            "posts": posts_with_score,
            "trending": [
                {
                    "tag": tag,
                    "count": count
                }
                for tag, count in trending_tags
            ]
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# REPORT USER
# =========================================
@search_bp.route("/report", methods=["POST"])
def report_user():
    try:

        data = request.json or {}

        username = data.get("username", "")
        reason = data.get("reason", "spam")

        db.collection("reports").add({
            "username": username,
            "reason": reason,
            "status": "pending",
            "createdAt": datetime.now(timezone.utc)
        })

        return jsonify({
            "message": f"User @{username} reported successfully"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
