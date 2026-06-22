# =========================================
# FILE: backend/ai/moderation_ai.py
# =========================================

class ModerationAI:

    def check_content(self, text):

        banned_words = ["hack", "malware"]

        for word in banned_words:
            if word in text.lower():
                return "Warning: Suspicious content detected."

        return "Content is safe."
