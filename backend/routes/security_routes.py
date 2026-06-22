# =========================================
# FILE: backend/api/security_routes.py
# =========================================

from flask import Blueprint, jsonify, request
from backend.security.threat_feed import ThreatFeed

# Initialize the feed globally so all routes share the same data state
feed = ThreatFeed()
security_bp = Blueprint("security", __name__)

# =========================================
# 🚨 GET ALL THREAT ALERTS
# =========================================
@security_bp.route("/threats", methods=["GET"])
def get_threats():
    try:
        # Returns the list of all current threats
        return jsonify(feed.get_latest_threats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# 🛡 GET CRITICAL THREATS ONLY
# =========================================
@security_bp.route("/threats/critical", methods=["GET"])
def get_critical():
    try:
        return jsonify(feed.get_critical_threats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# ➕ ADD NEW THREAT (Called by AI/Scanner)
# =========================================
@security_bp.route("/threats/add", methods=["POST"])
def add_threat():
    try:
        data = request.json
        if not data or "title" not in data:
            return jsonify({"error": "Missing title"}), 400
            
        feed.add_threat(
            title=data["title"],
            severity=data.get("severity", "MEDIUM"),
            category=data.get("category", "General")
        )
        return jsonify({"message": "Threat added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# 🧹 CLEAR ALL ALERTS
# =========================================
@security_bp.route("/threats/clear", methods=["POST"])
def clear_threats():
    try:
        feed.clear_threats()
        return jsonify({"message": "Threat feed cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
