# =========================================
# FILE: backend/api/ai_routes.py (FINAL + DATASET FIXED + CLEAN OUTPUT)
# =========================================

from flask import Blueprint, request, jsonify
import uuid

from backend.ai.core_ai import CoreAI
from backend.ai.image_generator import generate_image

from backend.security.link_scanner import scan_link
from backend.security.phishing_detector import detect_phishing
from backend.security.ai_scam_detector import detect_scam
from backend.security.cyber_score import calculate_score

from backend.firebase_client import db
from google.cloud import firestore

# ================= DATASET IMPORT =================
from backend.data_loader import search_all

ai_bp = Blueprint("ai", __name__)
AI_COLLECTION = "ai_chats"

ai_engine = CoreAI()


# =========================================
# HEALTH CHECK
# =========================================
@ai_bp.route("/test", methods=["GET"])
def test_ai():
    return jsonify({
        "success": True,
        "message": "NeuroAI backend running 🚀"
    })


# =========================================
# CHAT ENDPOINT (DATASET FIRST + AI FALLBACK)
# =========================================
@ai_bp.route("/chat", methods=["POST"])
def ai_chat():

    try:
        data = request.get_json(silent=True) or {}

        user_message = (data.get("message") or "").strip()
        username = data.get("username", "user")

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message required"
            }), 400

        # ================= SECURITY =================
        alerts = []

        if "http://" in user_message or "https://" in user_message:
            if not scan_link(user_message):
                alerts.append("⚠ Dangerous link detected")

        if detect_phishing(user_message):
            alerts.append("🎣 Possible phishing attempt detected")

        if detect_scam(user_message):
            alerts.append("🚨 Scam-like content detected")

        cyber_score = calculate_score(safe_login=True)

        # ================= IMAGE DETECTION =================
        response_type = "text"
        image_data = None

        lower_msg = user_message.lower()

        image_keywords = [
            "generate image",
            "create image",
            "draw",
            "image of",
            "make image",
            "show image",
            "picture of"
        ]

        if any(k in lower_msg for k in image_keywords):
            response_type = "image"

            try:
                image_url = generate_image(user_message)

                image_data = {
                    "prompt": user_message,
                    "url": f"http://127.0.0.1:5000{image_url}" if image_url else None,
                    "error": None if image_url else "Image generation failed"
                }

            except Exception as e:
                image_data = {
                    "prompt": user_message,
                    "url": None,
                    "error": str(e)
                }

        # ================= DATASET SEARCH =================
        dataset_results = search_all(user_message)

        dataset_used = False
        ai_response = ""

        # ================= PRIORITY: DATASET FIRST =================
        if dataset_results and len(dataset_results) > 0:

            dataset_used = True
            ai_response = "📚 DATASET RESULTS\n\n"

            for item in dataset_results[:5]:
                ai_response += f"🔹 CATEGORY: {item['category'].upper()}\n"

                data_item = item["data"]

                if isinstance(data_item, dict):
                    for k, v in list(data_item.items())[:10]:
                        ai_response += f"{k}: {v}\n"
                else:
                    ai_response += str(data_item)

                ai_response += "\n\n"

        else:
            # ================= AI FALLBACK =================
            try:
                ai_response = ai_engine.process(user_message)
            except Exception as e:
                ai_response = "AI processing error"
                alerts.append(str(e))

        # ================= FIREBASE SAVE =================
        try:
            db.collection(AI_COLLECTION).add({
                "id": str(uuid.uuid4()),
                "username": username,
                "message": user_message,
                "response": ai_response,
                "type": response_type,
                "image": image_data,
                "alerts": alerts,
                "cyber_score": cyber_score,
                "dataset_used": dataset_used,
                "createdAt": firestore.SERVER_TIMESTAMP
            })
        except Exception as db_err:
            print("Firebase error:", db_err)

        # ================= RESPONSE =================
        return jsonify({
            "success": True,
            "type": response_type,
            "message": user_message,
            "response": ai_response,
            "image": image_data,
            "alerts": alerts,
            "cyber_score": cyber_score,
            "dataset_used": dataset_used
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# HISTORY
# =========================================
@ai_bp.route("/history", methods=["GET"])
def get_history():

    try:
        chats = []

        for doc in db.collection(AI_COLLECTION).stream():
            data = doc.to_dict()
            data["id"] = doc.id
            chats.append(data)

        return jsonify({
            "success": True,
            "history": chats
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# DELETE CHAT
# =========================================
@ai_bp.route("/delete/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):

    try:
        db.collection(AI_COLLECTION).document(chat_id).delete()
        return jsonify({
            "success": True,
            "message": "Chat deleted"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# SECURITY CHECK
# =========================================
@ai_bp.route("/security-check", methods=["POST"])
def security_check():

    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")

        results = {
            "safe_link": True,
            "phishing_detected": False,
            "scam_detected": False,
            "alerts": []
        }

        if "http://" in text or "https://" in text:
            safe = scan_link(text)
            results["safe_link"] = safe

            if not safe:
                results["alerts"].append("Dangerous link detected")

        if detect_phishing(text):
            results["phishing_detected"] = True
            results["alerts"].append("Possible phishing attempt")

        if detect_scam(text):
            results["scam_detected"] = True
            results["alerts"].append("Scam-like content detected")

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
