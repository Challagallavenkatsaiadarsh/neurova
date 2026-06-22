import threading
import pyaudio


class AudioClient:

    def __init__(self):
        self.running = False
        self.thread = None

        # ================= AUDIO CONFIG =================
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.p = pyaudio.PyAudio()
        self.stream = None

    # ================= START AUDIO =================
    def start(self, room_id=None):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._capture_audio, args=(room_id,))
        self.thread.start()

        print(f"🎤 Audio started for room: {room_id}")

    # ================= AUDIO LOOP =================
    def _capture_audio(self, room_id):

        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        while self.running:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)

                # 🔥 HERE IS WHERE YOU WILL SEND TO SERVER
                # send_audio_to_backend(room_id, data)

            except Exception as e:
                print("Audio capture error:", e)
                break

    # ================= STOP AUDIO =================
    def stop(self):
        self.running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = None

        print("🔇 Audio stopped")
