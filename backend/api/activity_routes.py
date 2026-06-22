from flask import Blueprint, jsonify, request

from backend.core.activity_store import (
    add_activity,
    get_activity
)

activity_bp = Blueprint(
    "activity",
    __name__
)


# =====================================================
# ADD ACTIVITY
# =====================================================
@activity_bp.route(
    "/api/activity/add",
    methods=["POST"]
)
def api_add_activity():

    try:
        data = request.get_json() or {}

        activity_type = data.get("activity_type")
        user_id = data.get("user_id")
        post = data.get("post")

        if not activity_type:
            return jsonify({
                "success": False,
                "message": "activity_type missing"
            }), 400

        if not user_id:
            return jsonify({
                "success": False,
                "message": "user_id missing"
            }), 400

        if not post:
            return jsonify({
                "success": False,
                "message": "post missing"
            }), 400

        add_activity(
            activity_type,
            user_id,
            post
        )

        return jsonify({
            "success": True,
            "message": "Activity stored"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =====================================================
# GET ACTIVITY
# =====================================================
@activity_bp.route(
    "/api/activity/<activity_type>/<user_id>",
    methods=["GET"]
)
def api_get_activity(
    activity_type,
    user_id
):

    try:

        activities = get_activity(
            activity_type,
            user_id
        )

        return jsonify({
            "success": True,
            "activity_type": activity_type,
            "user_id": user_id,
            "count": len(activities),
            "items": activities
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =====================================================
# GET ALL USER ACTIVITIES
# =====================================================
@activity_bp.route(
    "/api/activity/all/<user_id>",
    methods=["GET"]
)
def api_get_all_activity(user_id):

    try:

        response = {
            "likes": get_activity("likes", user_id),
            "replies": get_activity("replies", user_id),
            "reposts": get_activity("reposts", user_id),
            "bookmarks": get_activity("bookmarks", user_id),
            "shares": get_activity("shares", user_id)
        }

        return jsonify({
            "success": True,
            "user_id": user_id,
            "data": response
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
