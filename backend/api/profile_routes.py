from flask import Blueprint, request, jsonify
from backend.firebase_client import db
from google.cloud import firestore

profile_bp = Blueprint("profile", __name__)

# --- Helper: Update User Lists (Follow/Following) ---
def update_user_list(user_id, target_id, list_name, add=True):
    user_ref = db.collection("users").document(user_id)
    if add:
        user_ref.update({list_name: firestore.ArrayUnion([target_id])})
    else:
        user_ref.update({list_name: firestore.ArrayRemove([target_id])})

# =====================================================
# TOGGLE ACTIVITY (Likes, Bookmarks, Reposts, Shares, Replies)
# =====================================================
@profile_bp.route("/toggle_activity", methods=["POST"])
def toggle_activity():
    try:
        data = request.json or {}
        uid = data.get("user_id")
        post_id = data.get("post_id")
        act_type = data.get("type") 
        post_data = data.get("post_data")

        act_ref = db.collection("users").document(uid).collection("activities")
        # Check if activity exists to toggle (Unlike/Unbookmark/Delete Reply)
        existing = act_ref.where("type", "==", act_type).where("post.id", "==", post_id).limit(1).get()

        if existing:
            for doc in existing:
                doc.reference.delete()
            return jsonify({"success": True, "action": "removed"})
        else:
            act_ref.add({
                "type": act_type,
                "post": post_data,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            return jsonify({"success": True, "action": "added"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =====================================================
# FOLLOW / UNFOLLOW
# =====================================================
@profile_bp.route("/follow", methods=["POST"])
def toggle_follow():
    data = request.json
    uid, target_id, action = data.get("user_id"), data.get("target_id"), data.get("action")
    is_following = (action == "follow")
    update_user_list(uid, target_id, "following_list", add=is_following)
    update_user_list(target_id, uid, "followers_list", add=is_following)
    return jsonify({"success": True, "is_following": is_following})

# =====================================================
# NOTIFICATIONS (SUBSCRIBE)
# =====================================================
@profile_bp.route("/subscribe", methods=["POST"])
def toggle_notifications():
    data = request.json
    uid, target_id = data.get("user_id"), data.get("target_id")
    sub_ref = db.collection("users").document(uid).collection("subscriptions").document(target_id)
    if data.get("enable"):
        sub_ref.set({"subscribed_at": firestore.SERVER_TIMESTAMP})
    else:
        sub_ref.delete()
    return jsonify({"success": True})

# =====================================================
# BLOCK / MUTE
# =====================================================
@profile_bp.route("/block/<target_id>", methods=["POST"])
def block_user(target_id):
    uid = request.json.get("current_user")
    db.collection("users").document(uid).collection("blocked").document(target_id).set({"at": firestore.SERVER_TIMESTAMP})
    return jsonify({"success": True})

@profile_bp.route("/mute", methods=["POST"])
def mute_user():
    data = request.json
    db.collection("users").document(data.get("user_id")).collection("muted").document(data.get("target_id")).set({"at": firestore.SERVER_TIMESTAMP})
    return jsonify({"success": True})

# =====================================================
# GET PROFILE (With Search and Activity Tabs)
# =====================================================
@profile_bp.route("/get", methods=["POST"])
def get_profile():
    try:
        data = request.json or {}
        uid, username = data.get("user_id"), data.get("username")
        
        user_doc = None
        user_data = None

        # Fetch by ID
        if uid:
            doc = db.collection("users").document(uid).get()
            if doc.exists:
                user_doc = doc
                user_data = doc.to_dict()

        # Search by Username
        if not user_data and username:
            users = db.collection("users").stream()
            for doc in users:
                doc_data = doc.to_dict()
                if doc_data.get("username", "").lower() == username.lower():
                    user_doc = doc
                    user_data = doc_data
                    uid = doc.id
                    break

        if not user_data:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Fetch Activities
        activities = []
        activity_docs = db.collection("users").document(uid).collection("activities").stream()
        for activity in activity_docs:
            act_data = activity.to_dict()
            activities.append({"activity_id": activity.id, **act_data})

        return jsonify({
            "success": True,
            "user": {
                **user_data, 
                "user_id": uid, 
                "followers_count": len(user_data.get("followers_list", [])), 
                "is_following": uid in user_data.get("followers_list", [])
            },
            "activity_tabs": {
                "all": activities,
                "likes": [a for a in activities if a["type"] == "likes"],
                "bookmarks": [a for a in activities if a["type"] == "bookmarks"],
                "reposts": [a for a in activities if a["type"] == "reposts"],
                "replies": [a for a in activities if a["type"] == "replies"],
                "shares": [a for a in activities if a["type"] == "shares"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =====================================================
# DELETE ACTIVITY (Specific ID)
# =====================================================
@profile_bp.route("/delete_activity", methods=["POST"])
def delete_activity():
    data = request.json
    try:
        db.collection("users").document(data.get("user_id")).collection("activities").document(data.get("activity_id")).delete()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/test", methods=["GET"])
def test_profile():
    return jsonify({"message": "Profile route working 🚀"})
