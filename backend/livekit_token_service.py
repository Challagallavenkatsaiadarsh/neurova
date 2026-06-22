from livekit.api import AccessToken, VideoGrants
import os
from datetime import timedelta


class LiveKitTokenService:

    def __init__(self):
        self.api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET", "devsecret")
        self.url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")

    def create_token(self, room: str, user: str, role: str = "listener"):

        try:
            # =========================
            # ROLE PERMISSIONS
            # =========================
            can_publish = role in ["speaker", "host"]

            grants = VideoGrants(
                room_join=True,
                room=room,
                can_publish=can_publish,
                can_subscribe=True
            )

            # =========================
            # TOKEN BUILD (SAFE MODE)
            # =========================
            token = AccessToken(self.api_key, self.api_secret)

            token.identity = user
            token.name = user
            token.grants = grants

            # ⚠️ IMPORTANT: ttl must be set BEFORE JWT generation
            token.ttl = timedelta(hours=6)

            jwt = token.to_jwt()

            return {
                "token": jwt,
                "url": self.url,
                "room": room,
                "user": user,
                "role": role
            }

        except Exception as e:
            import traceback
            print("🔥 LIVEKIT TOKEN ERROR:", str(e))
            print(traceback.format_exc())

            return {
                "error": str(e)
            }

    def create_join_token(self, room: str, user: str):
        return self.create_token(room, user, "listener")

    def create_speaker_token(self, room: str, user: str):
        return self.create_token(room, user, "speaker")

    def create_host_token(self, room: str, user: str):
        return self.create_token(room, user, "host")
