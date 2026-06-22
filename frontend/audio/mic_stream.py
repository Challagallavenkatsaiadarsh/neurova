import sounddevice as sd
import numpy as np
import base64
import threading
import queue
import time


class MicStream:

    def __init__(self, send_callback, user_id=None, space_id=None):

        self.send_callback = send_callback
        self.user_id = user_id
        self.space_id = space_id

        self.running = False
        self.stream = None

        # 🔥 audio buffer queue (prevents lag spikes)
        self.audio_queue = queue.Queue()

        # config
        self.samplerate = 16000   # lower = low latency (X Spaces style)
        self.channels = 1
        self.chunk_size = 1024

    # =========================================
    # AUDIO CAPTURE CALLBACK
    # =========================================
    def _callback(self, indata, frames, time_info, status):

        if not self.running:
            return

        # convert to bytes
        audio_chunk = indata.copy().tobytes()

        # encode (lightweight transport)
        encoded = base64.b64encode(audio_chunk).decode("utf-8")

        packet = {
            "type": "audio",
            "user": self.user_id,
            "space": self.space_id,
            "timestamp": time.time(),
            "data": encoded
        }

        # push to queue (non-blocking)
        self.audio_queue.put(packet)

    # =========================================
    # WORKER THREAD (SENDS AUDIO SMOOTHLY)
    # =========================================
    def _sender(self):

        while self.running:

            try:
                packet = self.audio_queue.get(timeout=1)
                self.send_callback(packet)

            except queue.Empty:
                continue

            except Exception:
                pass

    # =========================================
    # START MIC STREAM
    # =========================================
    def start(self):

        if self.running:
            return

        self.running = True

        # start sender thread
        threading.Thread(target=self._sender, daemon=True).start()

        # start mic stream
        self.stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.chunk_size,
            dtype=np.int16,
            callback=self._callback
        )

        self.stream.start()

        print("🎤 MicStream STARTED (X Spaces Mode)")

    # =========================================
    # STOP MIC STREAM
    # =========================================
    def stop(self):

        self.running = False

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except:
            pass

        print("🔇 MicStream STOPPED")
