from flask import Blueprint, jsonify, request
from backend.firebase_client import db
from google.cloud import firestore
from backend.security.cyber_score import calculate_score

user_bp = Blueprint("user", __name__)

USERS_COLLECTION = "users"


# =====================================================
# 🛡 GET CYBER SCORE
# =====================================================
@user_bp.route("/score", methods=["GET"])
def get_user_score():
    try:
        username = request.args.get("user", "user")

        result = calculate_score(
            safe_login=True,
            suspicious_links=0,
            reports=0,
            verified=True
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================
# ❤️ FOLLOW / UNFOLLOW TOGGLE
# =====================================================
@user_bp.route("/follow", methods=["POST"])
def follow_user():

    try:
        data = request.json or {}

        current_user_id = data.get("current_user_id")
        target_user_id = data.get("target_user_id")

        if not current_user_id or not target_user_id:
            return jsonify({
                "success": False,
                "message": "Missing user ids"
            }), 400

        if current_user_id == target_user_id:
            return jsonify({
                "success": False,
                "message": "You cannot follow yourself"
            }), 400

        current_ref = db.collection(USERS_COLLECTION).document(current_user_id)
        target_ref = db.collection(USERS_COLLECTION).document(target_user_id)

        current_doc = current_ref.get()
        target_doc = target_ref.get()

        if not current_doc.exists or not target_doc.exists:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        current_data = current_doc.to_dict()
        target_data = target_doc.to_dict()

        current_following = current_data.get("following_list", [])
        target_followers = target_data.get("followers_list", [])

        # =========================
        # UNFOLLOW
        # =========================
        if target_user_id in current_following:

            current_ref.update({
                "following_list": firestore.ArrayRemove([target_user_id]),
                "following_count": firestore.Increment(-1)
            })

            target_ref.update({
                "followers_list": firestore.ArrayRemove([current_user_id]),
                "followers_count": firestore.Increment(-1)
            })

            return jsonify({
                "success": True,
                "action": "unfollowed",
                "followers": max(0, target_data.get("followers_count", 0) - 1),
                "following": max(0, current_data.get("following_count", 0) - 1)
            })

        # =========================
        # FOLLOW
        # =========================
        current_ref.update({
            "following_list": firestore.ArrayUnion([target_user_id]),
            "following_count": firestore.Increment(1)
        })

        target_ref.update({
            "followers_list": firestore.ArrayUnion([current_user_id]),
            "followers_count": firestore.Increment(1)
        })

        return jsonify({
            "success": True,
            "action": "followed",
            "followers": target_data.get("followers_count", 0) + 1,
            "following": current_data.get("following_count", 0) + 1
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================================
# 🤝 MUTUAL FOLLOWERS
# =====================================================
@user_bp.route("/mutual/<user_id>", methods=["GET"])
def mutual_followers(user_id):

    try:
        current_user = request.args.get("current_user")

        if not current_user:
            return jsonify({
                "success": False,
                "message": "Missing current user"
            }), 400

        current_doc = db.collection(USERS_COLLECTION).document(current_user).get()
        target_doc = db.collection(USERS_COLLECTION).document(user_id).get()

        if not current_doc.exists or not target_doc.exists:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        current_following = set(current_doc.to_dict().get("following_list", []))
        target_followers = set(target_doc.to_dict().get("followers_list", []))

        mutual = list(current_following.intersection(target_followers))

        return jsonify({
            "success": True,
            "mutual_count": len(mutual),
            "mutual_users": mutual
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================
# 🚫 BLOCK USER
# =====================================================
@user_bp.route("/block/<user_id>", methods=["POST"])
def block_user(user_id):

    try:
        data = request.json or {}
        current_user = data.get("current_user")

        if not current_user:
            return jsonify({"success": False, "message": "Missing user"}), 400

        user_ref = db.collection(USERS_COLLECTION).document(current_user)

        user_ref.update({
            "blocked_users": firestore.ArrayUnion([user_id])
        })

        return jsonify({
            "success": True,
            "message": "User blocked",
            "blocked_user": user_id
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================
# 🚫 UNBLOCK USER
# =====================================================
@user_bp.route("/unblock/<user_id>", methods=["POST"])
def unblock_user(user_id):

    try:
        data = request.json or {}
        current_user = data.get("current_user")

        if not current_user:
            return jsonify({"success": False, "message": "Missing user"}), 400

        user_ref = db.collection(USERS_COLLECTION).document(current_user)

        user_ref.update({
            "blocked_users": firestore.ArrayRemove([user_id])
        })

        return jsonify({
            "success": True,
            "message": "User unblocked",
            "unblocked_user": user_id
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================
# 📋 GET BLOCKED USERS
# =====================================================
@user_bp.route("/blocked", methods=["GET"])
def get_blocked_users():

    try:
        current_user = request.args.get("user")

        if not current_user:
            return jsonify({"success": False, "message": "Missing user"}), 400

        doc = db.collection(USERS_COLLECTION).document(current_user).get()

        if not doc.exists:
            return jsonify({"success": True, "blocked_users": [], "count": 0})

        blocked = doc.to_dict().get("blocked_users", [])

        return jsonify({
            "success": True,
            "blocked_users": blocked,
            "count": len(blocked)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================
# 🧪 TEST ROUTE
# =====================================================
@user_bp.route("/test", methods=["GET"])
def test_user_routes():
    return jsonify({
        "message": "User system working 🚫"
    })
