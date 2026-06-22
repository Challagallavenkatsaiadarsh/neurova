# =========================================
# FILE: backend/main.py (FINAL FIXED + CLEAN ROUTING)
# =========================================

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, send_from_directory
import os
import traceback

import backend.config.cloudinary_config


# =========================
# ROUTES IMPORTS
# =========================
from backend.api.auth_routes import auth_bp
from backend.api.feed_routes import feed_bp
from backend.api.post_routes import post_bp
from backend.api.profile_routes import profile_bp
from backend.api.spaces_routes import spaces_bp
from backend.api.user_routes import user_bp
from backend.api.ai_routes import ai_bp
from backend.routes.security_routes import security_bp
from backend.api.safe_browser_routes import safe_browser_bp

# ✅ NEW: Activity Routes
from backend.api.activity_routes import activity_bp


# =========================
# OPTIONAL DATA ENGINE
# =========================
try:
    from backend.data_loader import search_all, get_dataset
    DATA_ENGINE = True
except Exception as e:
    print("[DATA ENGINE ERROR]", e)
    DATA_ENGINE = False


# =========================
# APP INIT
# =========================
app = Flask(__name__)
app.url_map.strict_slashes = False


# =========================
# GLOBAL ERROR HANDLER
# =========================
@app.errorhandler(Exception)
def handle_error(e):
    print("\n🔥 GLOBAL ERROR:")
    traceback.print_exc()
    return jsonify({
        "success": False,
        "error": str(e)
    }), 500


# =========================
# GENERATED FILES
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)


@app.route("/generated/<path:filename>")
def serve_generated_image(filename):
    return send_from_directory(GENERATED_DIR, filename, as_attachment=False)


# =========================
# BLUEPRINT REGISTRATION (ALL ROUTES)
# =========================

# 🔐 AUTH (signup, login, onboarding)
app.register_blueprint(auth_bp, url_prefix="/auth")

# 📰 FEED
app.register_blueprint(feed_bp, url_prefix="/feed")

# 📝 POSTS
app.register_blueprint(post_bp, url_prefix="/post")

# 👤 PROFILE
app.register_blueprint(profile_bp, url_prefix="/profile")

# 🌐 SPACES
app.register_blueprint(spaces_bp, url_prefix="/spaces")

# 👥 USERS
app.register_blueprint(user_bp, url_prefix="/user")

# 📊 ACTIVITIES (NEW)
app.register_blueprint(activity_bp)

# 🤖 AI FEATURES
app.register_blueprint(ai_bp, url_prefix="/ai")

# 🛡 SECURITY SYSTEM
app.register_blueprint(security_bp, url_prefix="/security")

# 🌍 SAFE BROWSER
app.register_blueprint(safe_browser_bp, url_prefix="/safe_browser")


# =========================
# ROUTE TEST (DEBUG)
# =========================
@app.route("/debug/routes")
def debug_routes():
    return jsonify({
        "routes": [
            {
                "endpoint": r.endpoint,
                "methods": list(r.methods),
                "rule": str(r)
            }
            for r in app.url_map.iter_rules()
        ]
    })


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return {
        "status": "Backend running 🚀",
        "auth_prefix": "/api/auth",
        "endpoints": {
            "login": "/api/auth/login",
            "signup": "/api/auth/signup",
            "onboarding": "/api/auth/complete-onboarding"
        },
        "data_engine": DATA_ENGINE,
        "activity": True,
        "safe_browser": True
    }


# =========================
# SEARCH ENGINE
# =========================
@app.route("/search")
def search():
    query = request.args.get("q", "")

    if not DATA_ENGINE:
        return jsonify({
            "error": "Data engine not loaded",
            "results": []
        })

    results = search_all(query)

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results
    })


# =========================
# DATA ENDPOINT
# =========================
@app.route("/data/<name>")
def data(name):

    if not DATA_ENGINE:
        return jsonify({"error": "Data engine not loaded"})

    try:
        return jsonify(get_dataset(name))
    except Exception as e:
        return jsonify({
            "error": "Dataset not found",
            "name": name,
            "details": str(e)
        })


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    print("\n🚀 SERVER STARTED ON http://127.0.0.1:5000")
    print("🔍 DEBUG: http://127.0.0.1:5000/debug/routes")
    print("🔐 AUTH BASE: http://127.0.0.1:5000/api/auth")
    print("📊 ACTIVITY SYSTEM ENABLED")
    print("🧠 ONBOARDING: /api/auth/complete-onboarding\n")

    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception:
        print("\n❌ SERVER FAILED")
        traceback.print_exc()
