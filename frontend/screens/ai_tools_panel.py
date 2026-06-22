# =========================================
# FILE: frontend/screens/ai_tools_panel.py
# =========================================

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton


class AIToolsPanel(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.spacing = 10

        tools = [
            "Search AI",
            "Cyber AI",
            "Trend AI",
            "Moderation AI"
        ]

        for tool in tools:
            self.add_widget(
                MDRaisedButton(
                    text=tool
                )
            )
