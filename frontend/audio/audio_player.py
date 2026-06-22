import sounddevice as sd
import numpy as np
import base64
import threading
import queue


class AudioPlayer:

    def __init__(self):

        # 🔥 match mic stream settings
        self.samplerate = 16000
        self.channels = 1

        # audio buffer queue (prevents lag + overlap issues)
        self.audio_queue = queue.Queue()

        self.running = True

        # start playback thread
        self.thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.thread.start()

        print("🔊 AudioPlayer READY (X Spaces Mode)")

    # =========================================
    # ADD AUDIO TO BUFFER
    # =========================================
    def play(self, encoded_audio):

        try:
            self.audio_queue.put(encoded_audio)

        except Exception as e:
            print("Queue error:", e)

    # =========================================
    # INTERNAL PLAYBACK LOOP
    # =========================================
    def _playback_loop(self):

        while self.running:

            try:
                encoded_audio = self.audio_queue.get(timeout=1)

                # decode base64 → bytes
                audio_bytes = base64.b64decode(encoded_audio)

                # convert bytes → int16 array (MATCH MIC STREAM)
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

                # normalize to float32 for smooth playback
                audio_float = audio_array.astype(np.float32) / 32768.0

                # 🔥 play WITHOUT interrupting previous audio
                sd.play(audio_float, self.samplerate, blocking=True)

            except queue.Empty:
                continue

            except Exception as e:
                print("Audio playback error:", e)

    # =========================================
    # STOP PLAYER
    # =========================================
    def stop(self):

        self.running = False

        try:
            sd.stop()
        except:
            pass
