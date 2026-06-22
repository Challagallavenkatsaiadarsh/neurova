from flask import Blueprint, jsonify, request
from backend.firebase_client import db
from google.cloud import firestore
import uuid
from datetime import datetime

report_bp = Blueprint("report", __name__)

REPORTS_COLLECTION = "reports"


# =========================
# 🚨 CREATE REPORT
# =========================
@report_bp.route("/report/<post_id>", methods=["POST"])
def report_post(post_id):
    try:
        data = request.json or {}

        reason = data.get("reason", "").strip().lower()
        reported_by = data.get("username", "user")

        # validation
        if not reason:
            return jsonify({"error": "Report reason is required"}), 400

        report = {
            "id": str(uuid.uuid4()),
            "post_id": post_id,
            "reported_by": reported_by,
            "reason": reason,
            "status": "pending",
            "createdAt": firestore.SERVER_TIMESTAMP
        }

        db.collection(REPORTS_COLLECTION).add(report)

        return jsonify({
            "message": "Post reported successfully",
            "post_id": post_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 📄 GET ALL REPORTS (ADMIN)
# =========================
@report_bp.route("/reports", methods=["GET"])
def get_reports():
    try:
        reports_ref = db.collection(REPORTS_COLLECTION).stream()

        reports = []

        for doc in reports_ref:
            report = doc.to_dict()
            report["id"] = doc.id
            reports.append(report)

        # sort newest first
        def sort_key(x):
            ts = x.get("createdAt")
            return ts.timestamp() if hasattr(ts, "timestamp") else 0

        reports.sort(key=sort_key, reverse=True)

        return jsonify({
            "reports": reports,
            "count": len(reports)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 🔄 UPDATE REPORT STATUS
# =========================
@report_bp.route("/report/<report_id>/status", methods=["PUT"])
def update_report_status(report_id):
    try:
        data = request.json or {}
        status = data.get("status", "").strip().lower()

        allowed_status = ["pending", "reviewed", "resolved", "rejected"]

        if status not in allowed_status:
            return jsonify({
                "error": f"Invalid status. Allowed: {allowed_status}"
            }), 400

        report_ref = db.collection(REPORTS_COLLECTION).document(report_id)

        if not report_ref.get().exists:
            return jsonify({"error": "Report not found"}), 404

        report_ref.update({
            "status": status,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "message": "Report status updated",
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ❌ DELETE REPORT (ADMIN ONLY)
# =========================
@report_bp.route("/report/<report_id>", methods=["DELETE"])
def delete_report(report_id):
    try:
        report_ref = db.collection(REPORTS_COLLECTION).document(report_id)

        if not report_ref.get().exists:
            return jsonify({"error": "Report not found"}), 404

        report_ref.delete()

        return jsonify({
            "message": "Report deleted successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 🔎 GET REPORTS BY POST
# =========================
@report_bp.route("/reports/post/<post_id>", methods=["GET"])
def get_reports_by_post(post_id):
    try:
        reports_ref = db.collection(REPORTS_COLLECTION).stream()

        reports = []

        for doc in reports_ref:
            report = doc.to_dict()
            report["id"] = doc.id

            if report.get("post_id") == post_id:
                reports.append(report)

        return jsonify({
            "post_id": post_id,
            "reports": reports,
            "count": len(reports)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# 🧪 TEST ROUTE
# =========================
@report_bp.route("/reports/test", methods=["GET"])
def test_reports():
    return jsonify({
        "message": "Report system working 🚨"
    })
