# =========================================
# LEVEL 4 STREAMING SERVER (CHATGPT STYLE)
# =========================================

from flask import Flask, request
from flask_socketio import SocketIO, emit
from backend.ai.core_ai import CoreAI
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ai = CoreAI()


@socketio.on("user_message")
def handle_message(data):

    message = data.get("message", "")

    response = ai.process(message)

    # =========================
    # STREAM RESPONSE WORD BY WORD
    # =========================
    for word in response.split():

        emit("ai_chunk", {"text": word + " "})
        time.sleep(0.05)

    emit("ai_done", {"status": "finished"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5005)
