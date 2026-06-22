from flask import Flask, request, jsonify
from livekit import api
from datetime import timedelta
import time
import traceback

app = Flask(__name__)

# =====================================================
# LIVEKIT CONFIG
# =====================================================

API_KEY = "devkey"

API_SECRET = "this_is_a_very_long_secure_dev_secret_key_123456"

LIVEKIT_URL = "ws://127.0.0.1:7880"

# =====================================================
# TOKEN ROUTE
# =====================================================

@app.route("/token", methods=["POST"])
def create_token():

    try:

        print("\n🔥 REQUEST HIT /token")

        data = request.get_json(force=True)

        print("📦 DATA:", data)

        user = str(data.get("user", "")).strip()

        room = str(data.get("room", "")).strip()

        role = str(data.get("role", "listener")).strip()

        if not user or not room:

            return jsonify({
                "error": "user and room required"
            }), 400

        print("🔑 Creating token...")

        # =====================================================
        # ACCESS TOKEN
        # =====================================================

        token = api.AccessToken(
            api_key=API_KEY,
            api_secret=API_SECRET
        )

        token.with_identity(user)

        token.with_name(user)

        # =====================================================
        # VIDEO GRANTS
        # =====================================================

        grants = api.VideoGrants(
            room_join=True,
            room=room,
            room_create=True,
            can_publish=True,
            can_publish_data=True,
            can_subscribe=True
        )

        token.with_grants(grants)

        token.with_ttl(timedelta(hours=5))

        jwt_token = token.to_jwt()

        print("✅ TOKEN GENERATED")

        return jsonify({

            "token": jwt_token,

            "url": LIVEKIT_URL,

            "user": user,

            "room": room,

            "role": role,

            "issued_at": int(time.time())
        })

    except Exception as e:

        print("\n❌ FULL ERROR:")

        print(traceback.format_exc())

        return jsonify({
            "error": str(e)
        }), 500


# =====================================================
# HEALTH
# =====================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    print("🎤 Token server running on http://127.0.0.1:5002")

    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )
