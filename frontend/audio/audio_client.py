import asyncio
import threading
import numpy as np
import sounddevice as sd
from datetime import datetime
import time

from livekit import rtc
from db import Database


class AudioClient:

    def __init__(self):
        self.room = None
        self.token = None
        self.ws_url = None

        self.audio_source = None
        self.local_track = None

        self.running = False
        self.muted = False

        # ================= SPEAKING STATE =================
        self.is_speaking = False
        self.remote_speakers = set()   # 🔴 real-time active speakers

        # fallback / tracking
        self.remote_users = set()

        # volume tracking (optional UI)
        self.user_volume = {}

        # speaker output
        self.speaker_stream = None

        # asyncio loop
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, daemon=True).start()

    # ================= LOOP =================
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # ================= DB LOG =================
    async def _log_event(self, room_id, user_id, event_type):
        try:
            await Database.execute("""
                INSERT INTO voice_events(room_id, user_id, event_type, created_at)
                VALUES($1, $2, $3, $4)
            """, room_id, user_id, event_type, datetime.utcnow())
        except Exception as e:
            print("DB log error:", e)

    def log_event(self, room_id, user_id, event_type):
        asyncio.run_coroutine_threadsafe(
            self._log_event(room_id, user_id, event_type),
            self.loop
        )

    # ================= START =================
    def start(self, room_id, token, ws_url="ws://127.0.0.1:7880"):

        self.token = token
        self.ws_url = ws_url
        self.room_id = room_id

        self.log_event(room_id, "SYSTEM", "room_start")

        asyncio.run_coroutine_threadsafe(
            self._connect(room_id),
            self.loop
        )

    # ================= CONNECT =================
    async def _connect(self, room_id):

        print("🎤 Connecting to LiveKit...")

        self.room = rtc.Room()
        await self.room.connect(self.ws_url, self.token)

        print("✅ Connected:", room_id)

        self.audio_source = rtc.AudioSource(
            sample_rate=48000,
            num_channels=1
        )

        self.local_track = rtc.LocalAudioTrack.create_audio_track(
            "mic",
            self.audio_source
        )

        await self.room.local_participant.publish_track(self.local_track)

        self.running = True

        threading.Thread(target=self._capture_mic, daemon=True).start()

        self._init_speaker()
        self._setup_remote_audio()

        self.log_event(room_id, "SYSTEM", "room_connected")

    # ================= MICROPHONE =================
    def _capture_mic(self):

        def callback(indata, frames, time_info, status):

            if not self.running or self.muted:
                return

            audio = indata[:, 0].astype(np.float32)

            # send audio to LiveKit
            asyncio.run_coroutine_threadsafe(
                self.audio_source.capture_frame(audio),
                self.loop
            )

            # ================= VAD (VOICE ACTIVITY DETECTION) =================
            volume = np.linalg.norm(audio)

            speaking_now = volume > 0.02  # 🔥 threshold (tune this)

            # track self speaking state (push-to-talk / mic activity)
            if speaking_now != self.is_speaking:
                self.is_speaking = speaking_now
                self.send_speaking_event(speaking_now)

        with sd.InputStream(
            channels=1,
            samplerate=48000,
            callback=callback
        ):
            while self.running:
                sd.sleep(50)

    # ================= SPEAKING EVENT =================
    def send_speaking_event(self, state: bool):

        try:
            self.room.local_participant.publish_data(
                f"speaking:{int(state)}".encode(),
                reliable=False
            )
        except Exception as e:
            print("Speaking event error:", e)

    # ================= SPEAKER OUTPUT =================
    def _init_speaker(self):

        self.speaker_stream = sd.OutputStream(
            samplerate=48000,
            channels=1,
            dtype="float32",
            blocksize=960
        )

        self.speaker_stream.start()
        print("🔊 Speaker ready")

    # ================= REMOTE AUDIO =================
    def _setup_remote_audio(self):

        @self.room.on("participant_connected")
        def on_join(participant):
            print("🟢 Joined:", participant.identity)
            self.remote_users.add(participant.identity)

            self.log_event(self.room_id, participant.identity, "join_voice")

        @self.room.on("participant_disconnected")
        def on_leave(participant):
            print("🔴 Left:", participant.identity)

            self.remote_users.discard(participant.identity)
            self.remote_speakers.discard(participant.identity)

            self.log_event(self.room_id, participant.identity, "leave_voice")

        @self.room.on("track_subscribed")
        def on_track(track, publication, participant):

            if track.kind.name == "AUDIO":

                identity = participant.identity
                print("🔊 Audio from:", identity)

                self.remote_users.add(identity)

                audio_stream = rtc.AudioStream(track)

                # mark speaker ACTIVE immediately
                self._mark_speaking(identity)

                async def play():
                    async for frame in audio_stream:

                        audio_data = getattr(frame, "data", None)
                        if audio_data is None:
                            continue

                        try:
                            pcm = np.frombuffer(audio_data, dtype=np.float32)

                            if pcm.size == 0:
                                continue

                            # update volume tracking
                            vol = np.linalg.norm(pcm)
                            self.user_volume[identity] = vol

                            # 🔥 speaking detection per remote user
                            if vol > 0.015:
                                self._mark_speaking(identity)

                            self.speaker_stream.write(pcm)

                        except Exception as e:
                            print("Audio error:", e)

                asyncio.create_task(play())

    # ================= SPEAKING TRACKER =================
    def _mark_speaking(self, user_id):

        self.remote_speakers.add(user_id)

        # auto cleanup after silence
        def remove_after_timeout(uid):
            time.sleep(2.0)
            self.remote_speakers.discard(uid)

        threading.Thread(
            target=remove_after_timeout,
            args=(user_id,),
            daemon=True
        ).start()

    # ================= MUTE =================
    def mute(self):
        self.muted = True
        print("🔇 Muted")
        self.log_event(self.room_id, "SELF", "mute")

    def unmute(self):
        self.muted = False
        print("🎤 Unmuted")
        self.log_event(self.room_id, "SELF", "unmute")

    # ================= HOST CONTROL =================
    def mute_remote(self, user_id):
        print(f"🔇 Mute request: {user_id}")
        self.log_event(self.room_id, user_id, "host_mute")

    def kick_remote(self, user_id):
        print(f"🚫 Kick request: {user_id}")
        self.log_event(self.room_id, user_id, "host_kick")

    def promote_remote(self, user_id):
        print(f"⭐ Promote: {user_id}")
        self.log_event(self.room_id, user_id, "host_promote")

    # ================= STOP =================
    def stop(self):

        self.running = False

        self.log_event(self.room_id, "SYSTEM", "room_stop")

        try:
            if self.speaker_stream:
                self.speaker_stream.stop()
                self.speaker_stream.close()

            if self.room:
                asyncio.run_coroutine_threadsafe(
                    self.room.disconnect(),
                    self.loop
                )

            print("🔇 Disconnected")

        except Exception as e:
            print("Stop error:", e)
