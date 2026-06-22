# =========================================
# FILE: frontend/screens/ai_chat_widget.py
# =========================================

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


class AIChatWidget(MDCard):

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)

        self.padding = 15
        self.radius = [15]
        self.size_hint_y = None
        self.height = 100

        self.add_widget(
            MDLabel(
                text=text
            )
        )
