# =========================================
# FILE: frontend/screens/cyber_score_screen.py 
# =========================================

import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.app import App

class CyberScoreScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.root = MDBoxLayout(orientation="vertical", padding=20, spacing=20)
        self.add_widget(self.root)
        
        # Initial UI elements
        self.title = MDLabel(text="🛡 Cyber Shield Score", halign="center", font_style="H4")
        self.loading_label = MDLabel(text="Loading your security status...", halign="center")
        
        self.root.add_widget(self.title)
        self.root.add_widget(self.loading_label)

    def on_enter(self):
        """Triggered automatically when screen is opened."""
        app = App.get_running_app()
        
        # 1. Try to get data from app cache (instant)
        if hasattr(app, 'user_data') and app.user_data:
            # Map the login structure to our UI labels
            mapped_data = {
                "score": app.user_data.get("cyber_score", 0),
                "status": app.user_data.get("security_status", "Unknown")
            }
            self.build_ui(mapped_data)
        else:
            # 2. Fallback to network if cache is empty
            Clock.schedule_once(lambda dt: self.fetch_score(), 0.1)

    def fetch_score(self):
        """Fetch the dynamic score from the backend API if cache is missing."""
        try:
            url = "http://127.0.0.1:5000/api/user/score"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                Clock.schedule_once(lambda dt: self.build_ui(data))
            else:
                self.loading_label.text = f"Error: Received status {response.status_code}"
        except Exception as e:
            self.loading_label.text = f"Connection Error: {e}"

    def build_ui(self, result):
        """Dynamically render the UI with data."""
        self.root.clear_widgets()
        
        self.root.add_widget(MDLabel(text="🛡 Cyber Shield Score", halign="center", font_style="H4"))

        score_card = MDCard(
            orientation="vertical", padding=25, radius=[25],
            size_hint=(1, None), height=250, md_bg_color=(0.05, 0.09, 0.08, 1)
        )

        score_label = MDLabel(
            text=f"{result.get('score', 0)}",
            halign="center", font_style="H1",
            theme_text_color="Custom", text_color=(0.25, 0.85, 0.65, 1)
        )

        status_label = MDLabel(text=result.get("status", "Unknown"), halign="center", font_style="H5")
        info_label = MDLabel(text="Your account security is monitored by Neurova.", halign="center", theme_text_color="Secondary")

        score_card.add_widget(score_label)
        score_card.add_widget(status_label)
        score_card.add_widget(info_label)

        self.root.add_widget(score_card)
