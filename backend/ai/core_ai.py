# =========================================
# FILE: backend/ai/core_ai.py (LEVEL 9 READY CORE)
# =========================================

import requests
import json


class CoreAI:

    def __init__(self):

        # =========================================
        # OLLAMA ENDPOINT
        # =========================================
        self.url = "http://localhost:11434/api/generate"

        # =========================================
        # PRIMARY MODEL
        # =========================================
        self.model = "phi3"

        # =========================================
        # FALLBACK MODEL (future upgrade)
        # =========================================
        self.fallback_model = "llama3"

        print("🧠 NeuroAI Core Engine Initialized (Level 9 Ready)")

    # =========================================
    # NORMAL AI RESPONSE
    # =========================================
    def process(self, message):

        if not message:
            return "Please enter a message."

        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=180
            )

            # =========================================
            # MODEL NOT FOUND FIX
            # =========================================
            if response.status_code == 404:
                return (
                    "❌ Model Not Found in Ollama\n\n"
                    "Fix:\n"
                    f"  ollama run {self.model}\n\n"
                    "Check models:\n"
                    "  ollama list"
                )

            # =========================================
            # OTHER HTTP ERRORS
            # =========================================
            if response.status_code != 200:
                try:
                    err = response.json()
                except Exception:
                    err = response.text

                return f"AI Server Error:\n{err}"

            # =========================================
            # PARSE RESPONSE
            # =========================================
            data = response.json()
            result = data.get("response", "")

            if not result:
                return "⚠ AI returned empty response."

            return result.strip()

        # =========================================
        # OLLAMA NOT RUNNING
        # =========================================
        except requests.exceptions.ConnectionError:
            return (
                "🚨 Ollama Not Running\n\n"
                "Start it using:\n"
                "  ollama serve\n\n"
                f"Or run model:\n"
                f"  ollama run {self.model}"
            )

        # =========================================
        # TIMEOUT
        # =========================================
        except requests.exceptions.Timeout:
            return (
                "⏳ AI Timeout\n\n"
                "Model too slow.\n"
                "Try shorter prompt or switch model:\n"
                "phi3 → llama3"
            )

        # =========================================
        # GENERAL ERROR
        # =========================================
        except Exception as e:
            return f"AI Error: {str(e)}"

    # =========================================
    # STREAMING RESPONSE (LEVEL 9 CORE)
    # =========================================
    def stream(self, message):

        payload = {
            "model": self.model,
            "prompt": message,
            "stream": True
        }

        try:
            with requests.post(self.url, json=payload, stream=True, timeout=300) as r:

                for line in r.iter_lines():

                    if not line:
                        continue

                    try:
                        decoded = line.decode("utf-8")

                        # Ollama streams JSON chunks line by line
                        data = json.loads(decoded)

                        chunk = data.get("response", "")

                        if chunk:
                            yield chunk

                    except Exception:
                        continue

        except Exception:
            yield "Streaming failed."
