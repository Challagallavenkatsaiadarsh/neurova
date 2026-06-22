# =========================================
# FILE: voice.py
# FULL UPDATED + FIXED VERSION
# =========================================

import speech_recognition as sr
import pyttsx3
import time
import threading
import socketio


class VoiceEngine:

    def __init__(
        self,
        room_id=None,
        user_id=None,
        server_url="http://127.0.0.1:5000"
    ):

        # =========================================
        # TTS ENGINE (SAFE INIT)
        # =========================================
        self.tts = None

        try:
            # Windows SAPI5
            self.tts = pyttsx3.init(driverName='sapi5')

        except Exception as e:

            print("⚠️ SAPI5 failed:", e)

            try:
                self.tts = pyttsx3.init()

            except Exception as e2:
                print("❌ Voice engine disabled:", e2)
                self.tts = None

        # =========================================
        # RECOGNIZER
        # =========================================
        self.r = sr.Recognizer()

        self.r.dynamic_energy_threshold = True
        self.r.pause_threshold = 0.8
        self.r.non_speaking_duration = 0.5

        # =========================================
        # LIVE STATE
        # =========================================
        self.room_id = room_id
        self.user_id = user_id

        self.is_speaking = False
        self.last_emit_time = 0
        self.last_audio_time = 0
        self.volume_level = 0.0

        # =========================================
        # SAFETY FLAG
        # =========================================
        self.force_stop = False

        # =========================================
        # SOCKET
        # =========================================
        self.sio = socketio.Client()

        try:
            self.sio.connect(server_url)

        except Exception as e:
            print("⚠️ Socket connection failed:", e)

        # =========================================
        # SOCKET LISTENERS
        # =========================================
        @self.sio.on("participant_update")
        def on_participant(data):
            pass

        @self.sio.on("live_speaking")
        def on_live_speaking(data):
            pass

        # =========================================
        # BACKGROUND THREADS
        # =========================================
        threading.Thread(
            target=self._watchdog_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        ).start()

    # =========================================
    # TEXT TO SPEECH
    # =========================================
    def speak(self, text: str):

        if not text:
            return

        if not self.tts:
            print("🔇 TTS disabled:", text)
            return

        try:
            self.tts.say(str(text))
            self.tts.runAndWait()

        except Exception as e:
            print("⚠️ Speak failed:", e)

    # =========================================
    # SPEECH TO TEXT
    # FIXED VERSION
    # =========================================
    def listen(self):

        with sr.Microphone() as source:

            print("🎤 Calibrating mic...")

            self.r.adjust_for_ambient_noise(
                source,
                duration=1
            )

            try:

                # =========================================
                # LISTEN
                # =========================================
                audio = self.r.listen(
                    source,
                    timeout=6,
                    phrase_time_limit=6
                )

                # =========================================
                # VOLUME
                # =========================================
                volume = self._estimate_volume(
                    audio.frame_data
                )

                self._emit_speaking(
                    True,
                    volume
                )

                self.last_audio_time = time.time()

                # =========================================
                # GOOGLE SPEECH RECOGNITION
                # =========================================
                text = self.r.recognize_google(
                    audio,
                    language="en-IN"
                )

                # =========================================
                # SAFE STRING FIX
                # =========================================
                text = str(text).lower().strip()

                self._safe_stop_speaking()

                if text:
                    print("🧠", text)

                # =========================================
                # RETURN STRING
                # =========================================
                return text

            except sr.WaitTimeoutError:

                self._safe_stop_speaking()

                return ""

            except sr.UnknownValueError:

                self._safe_stop_speaking()

                return ""

            except Exception as e:

                print("Voice Error:", e)

                self._safe_stop_speaking()

                return ""

    # =========================================
    # VOLUME ESTIMATION
    # =========================================
    def _estimate_volume(self, raw_audio):

        try:
            import numpy as np

            audio = np.frombuffer(
                raw_audio,
                dtype=np.int16
            )

            volume = abs(audio).mean() / 32768

            return min(float(volume), 1.0)

        except Exception as e:

            print("Volume Error:", e)

            return 0.0

    # =========================================
    # EMIT SPEAKING STATE
    # =========================================
    def _emit_speaking(self, is_speaking, volume):

        if not self.sio.connected:
            return

        try:

            self.sio.emit(
                "speaking",
                {
                    "room": self.room_id,
                    "user": self.user_id,
                    "is_speaking": is_speaking,
                    "volume": volume
                }
            )

            self.is_speaking = is_speaking
            self.volume_level = volume
            self.last_emit_time = time.time()

        except Exception as e:

            print("Socket Emit Error:", e)

    # =========================================
    # SAFE STOP SPEAKING
    # =========================================
    def _safe_stop_speaking(self):

        if self.is_speaking:

            try:
                self._emit_speaking(False, 0.0)

            except:
                pass

        self.is_speaking = False
        self.volume_level = 0.0

    # =========================================
    # HEARTBEAT LOOP
    # =========================================
    def _heartbeat_loop(self):

        while not self.force_stop:

            time.sleep(1.5)

            if self.is_speaking:

                if (
                    time.time() -
                    self.last_audio_time
                ) > 2.0:

                    self._safe_stop_speaking()

    # =========================================
    # WATCHDOG LOOP
    # =========================================
    def _watchdog_loop(self):

        while not self.force_stop:

            time.sleep(2)

            if (
                self.is_speaking and
                (
                    time.time() -
                    self.last_emit_time
                ) > 3
            ):

                print("🧹 Resetting stale speaking state")

                self._safe_stop_speaking()

    # =========================================
    # STOP ENGINE
    # =========================================
    def stop(self):

        self.force_stop = True

        try:

            self._safe_stop_speaking()

            if self.sio.connected:
                self.sio.disconnect()

        except Exception as e:

            print("Stop Error:", e)
