# =========================================
# FILE: backend/ai/agent_engine.py (LEVEL 12 FINAL CONNECTED)
# =========================================

from backend.ai.core_ai import CoreAI
from backend.ai.memory_store import MemoryStore
from backend.security.link_scanner import scan_link
from backend.tools.web_search import search_web
from backend.ai.image_generator import ImageGenerator
from backend.ai.voice import VoiceEngine


class AgentEngine:

    def __init__(self):

        # =========================================
        # CORE MODULES
        # =========================================
        self.ai = CoreAI()
        self.memory = MemoryStore()
        self.image = ImageGenerator()

        # =========================================
        # VOICE ENGINE
        # =========================================
        self.voice = VoiceEngine()

        print("🧠 Neurova LEVEL 12 AGENT ENGINE ACTIVE")

    # =========================================
    # MAIN ENTRY POINT
    # =========================================
    def run(self, message: str, user_id="default"):

        if not message:
            return {"type": "text", "data": "Please enter a message"}

        msg = message.lower().strip()

        # =========================================
        # MEMORY SAVE (NORMAL TEXT)
        # =========================================
        self.memory.save(user_id, message)

        # =========================================
        # 🔥 HASHTAG SEARCH MODE (#topic)
        # =========================================
        if msg.startswith("#"):
            tag = msg.replace("#", "").strip()

            # fetch from memory
            history = self.memory.get(user_id)

            results = [
                m for m in history
                if tag in m.lower()
            ]

            return {
                "type": "search",
                "data": results if results else ["No posts found for #" + tag]
            }

        # =========================================
        # SECURITY CHECK
        # =========================================
        if "http" in msg and not scan_link(msg):
            return {
                "type": "warning",
                "data": "🚨 Unsafe link detected"
            }

        # =========================================
        # TOOL PLANNER
        # =========================================
        plan = self.plan(msg)

        if plan == "image":
            return self.handle_image(message)

        elif plan == "search":
            return self.handle_search(message)

        elif plan == "multi":
            return self.handle_multi(message, user_id)

        return self.handle_ai(message, user_id)

    # =========================================
    # TOOL DECISION ENGINE
    # =========================================
    def plan(self, msg):

        prompt = f"""
Decide tool:
User: {msg}

Return ONLY:
ai / search / image / multi
"""

        return self.ai.process(prompt).lower().strip()

    # =========================================
    # MULTI TOOL ENGINE
    # =========================================
    def handle_multi(self, message, user_id):

        search_results = search_web(message)

        summary = self.ai.process(f"""
Summarize:

{search_results}

User:
{message}
""")

        image = self.image.generate(message)

        return {
            "type": "multi",
            "data": {
                "search": search_results,
                "summary": summary,
                "image": image
            }
        }

    # =========================================
    # AI CHAT MODE
    # =========================================
    def handle_ai(self, message, user_id):

        history = self.memory.get(user_id)
        context = "\n".join(history[-15:])

        prompt = f"""
You are Neurova AI.

Be smart, short, helpful.

Conversation history:
{context}

User:
{message}
"""

        response = self.ai.process(prompt)

        return {
            "type": "text",
            "data": response
        }

    # =========================================
    # IMAGE MODE
    # =========================================
    def handle_image(self, message):

        prompt = message.replace("generate", "").strip() or message

        image = self.image.generate(prompt)

        if not image:
            return {
                "type": "warning",
                "data": "🖼 Image generation failed"
            }

        return {
            "type": "image",
            "data": {
                "image": image,
                "prompt": prompt
            }
        }

    # =========================================
    # SEARCH MODE
    # =========================================
    def handle_search(self, message):

        results = search_web(message)

        return {
            "type": "search",
            "data": results or []
        }

    # =========================================
    # VOICE CONNECTED
    # =========================================
    def speak(self, text: str):
        """Text → Speech"""
        self.voice.speak(text)

    def listen(self) -> str:
        """Speech → Text"""
        return self.voice.listen()
