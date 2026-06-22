# =========================================
# FILE: frontend/screens/ai_search_panel.py
# =========================================

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField


class AISearchPanel(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.add_widget(
            MDTextField(
                hint_text="Search AI topics..."
            )
        )
