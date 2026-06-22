import asyncio
import threading
import numpy as np
import sounddevice as sd

from livekit import rtc


class LiveKitAudioClient:

    def __init__(self):
        self.room = None
        self.audio_source = None
        self.track = None
        self.running = False
        self.loop = asyncio.new_event_loop()

        threading.Thread(target=self._run_loop, daemon=True).start()

    # ================= LOOP =================
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # ================= START =================
    def start(self, room_id, token, ws_url="ws://127.0.0.1:7880"):

        asyncio.run_coroutine_threadsafe(
            self._start(room_id, token, ws_url),
            self.loop
        )

    # ================= CONNECT =================
    async def _start(self, room_id, token, ws_url):

        print("🎤 Connecting to LiveKit...")

        self.room = rtc.Room()
        await self.room.connect(ws_url, token)

        print("✅ Connected to room:", room_id)

        # ================= AUDIO SOURCE =================
        self.audio_source = rtc.AudioSource(
            sample_rate=48000,
            num_channels=1
        )

        self.track = rtc.LocalAudioTrack.create_audio_track(
            "mic",
            self.audio_source
        )

        await self.room.local_participant.publish_track(self.track)

        print("🎙️ Microphone publishing started")

        # start mic capture thread
        self.running = True
        threading.Thread(target=self._capture_mic, daemon=True).start()

    # ================= MICROPHONE CAPTURE =================
    def _capture_mic(self):

        def callback(indata, frames, time, status):
            if not self.running:
                return

            audio = indata[:, 0].astype(np.float32)

            # push to LiveKit
            asyncio.run_coroutine_threadsafe(
                self.audio_source.capture_frame(audio),
                self.loop
            )

        with sd.InputStream(
            channels=1,
            samplerate=48000,
            callback=callback
        ):
            while self.running:
                sd.sleep(100)

    # ================= STOP =================
    def stop(self):

        self.running = False

        if self.room:
            asyncio.run_coroutine_threadsafe(
                self.room.disconnect(),
                self.loop
            )

        print("🔇 Voice stopped")
