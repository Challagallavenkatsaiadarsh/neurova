from flask import Blueprint, request, jsonify
from google.cloud import firestore
import uuid
import cloudinary.uploader

from backend.firebase_client import db

post_bp = Blueprint("post", __name__)

POSTS_COLLECTION = "posts"


# =========================
# CREATE POST (TEXT + IMAGE - CLOUDINARY FIX)
# =========================
@post_bp.route("/create", methods=["POST"])
def create_post():
    try:

        # =========================
        # TEXT DATA
        # =========================
        username = request.form.get("username", "user")
        text = request.form.get("text", "")

        image_url = ""

        # =========================
        # IMAGE UPLOAD (CLOUDINARY)
        # =========================
        if "image" in request.files:
            image = request.files["image"]

            if image and image.filename != "":

                upload_result = cloudinary.uploader.upload(
                    image,
                    folder="neurova_posts"
                )

                image_url = upload_result.get("secure_url", "")

        # =========================
        # POST DATA
        # =========================
        post = {
            "username": username,
            "text": text,
            "image": image_url,   # Cloudinary URL
            "likes": [],
            "comments": [],
            "reposts": [],
            "bookmarks": [],
            "shares": 0,
            "createdAt": firestore.SERVER_TIMESTAMP
        }

        doc_ref = db.collection(POSTS_COLLECTION).add(post)

        return jsonify({
            "success": True,
            "message": "Post created successfully",
            "post_id": doc_ref[1].id,
            "image": image_url
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# LIKE / UNLIKE POST
# =========================
@post_bp.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    try:
        data = request.json or {}
        username = data.get("username", "user")

        post_ref = db.collection(POSTS_COLLECTION).document(post_id)
        doc = post_ref.get()

        if not doc.exists:
            return jsonify({"error": "Post not found"}), 404

        post = doc.to_dict()
        likes = post.get("likes", [])

        if username in likes:
            post_ref.update({
                "likes": firestore.ArrayRemove([username])
            })
            action = "unliked"
        else:
            post_ref.update({
                "likes": firestore.ArrayUnion([username])
            })
            action = "liked"

        updated = post_ref.get().to_dict()

        return jsonify({
            "message": f"Post {action}",
            "likes_count": len(updated.get("likes", []))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ADD COMMENT
# =========================
@post_bp.route("/comment/<post_id>", methods=["POST"])
def add_comment(post_id):
    try:
        data = request.json
        username = data.get("username", "user")
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Comment cannot be empty"}), 400

        post_ref = db.collection(POSTS_COLLECTION).document(post_id)
        doc = post_ref.get()

        if not doc.exists:
            return jsonify({"error": "Post not found"}), 404

        comment = {
            "id": str(uuid.uuid4()),
            "username": username,
            "text": text,
            "createdAt": firestore.SERVER_TIMESTAMP
        }

        post_ref.update({
            "comments": firestore.ArrayUnion([comment])
        })

        return jsonify({
            "message": "Comment added",
            "comment": comment
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# GET SINGLE POST
# =========================
@post_bp.route("/<post_id>", methods=["GET"])
def get_post(post_id):
    try:
        doc = db.collection(POSTS_COLLECTION).document(post_id).get()

        if not doc.exists:
            return jsonify({"error": "Post not found"}), 404

        post = doc.to_dict()
        post["id"] = doc.id

        return jsonify(post)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# GET ALL POSTS
# =========================
@post_bp.route("/all", methods=["GET"])
def get_all_posts():
    try:
        posts_ref = db.collection(POSTS_COLLECTION).stream()

        posts = []
        for doc in posts_ref:
            post = doc.to_dict()
            post["id"] = doc.id
            posts.append(post)

        return jsonify({"posts": posts[::-1]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# DELETE POST
# =========================
@post_bp.route("/delete/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        doc_ref = db.collection(POSTS_COLLECTION).document(post_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Post not found"}), 404

        doc_ref.delete()

        return jsonify({"message": "Post deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
