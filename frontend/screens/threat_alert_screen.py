# =========================================
# FILE: frontend/screens/threat_alert_screen.py
# =========================================

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView

from kivy.graphics import Rectangle
from kivy.clock import Clock

import threading
import requests


class ThreatAlertScreen(MDScreen):

    API_URL = "http://127.0.0.1:5000/security/threats"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # =========================================
        # BACKGROUND
        # =========================================
        with self.canvas.before:
            self.bg = Rectangle(
                source=r"C:\Users\Admin\Documents\neurova\frontend\assets\images\threat_alert_bg.png",
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        # =========================================
        # ROOT
        # =========================================
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        # =========================================
        # HEADER
        # =========================================
        title = MDLabel(
            text="🚨 Live Threat Alerts",
            halign="center",
            bold=True,
            font_style="H5",
            size_hint_y=None,
            height=60,
            theme_text_color="Custom",
            text_color=(1, 0.35, 0.35, 1)
        )

        self.root_layout.add_widget(title)

        # =========================================
        # SCROLL AREA
        # =========================================
        self.scroll = MDScrollView()

        self.content = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            adaptive_height=True,
            size_hint_y=None
        )

        self.content.bind(minimum_height=self.content.setter("height"))

        self.scroll.add_widget(self.content)
        self.root_layout.add_widget(self.scroll)

        self.add_widget(self.root_layout)

        # =========================================
        # LOAD DATA FROM BACKEND
        # =========================================
        self.load_threats()

        # 🔥 AUTO REFRESH EVERY 5 SEC (LIVE FEEL)
        Clock.schedule_interval(lambda dt: self.load_threats(), 5)

    # =========================================
    # LOAD THREATS FROM API
    # =========================================
    def load_threats(self):

        def worker():
            try:
                res = requests.get(self.API_URL, timeout=10)
                alerts = res.json()
            except:
                alerts = []

            Clock.schedule_once(lambda dt: self.update_ui(alerts))

        threading.Thread(target=worker, daemon=True).start()

    # =========================================
    # UPDATE UI
    # =========================================
    def update_ui(self, alerts):

        self.content.clear_widgets()

        for alert in alerts:

            card = MDCard(
                orientation="vertical",
                padding=15,
                spacing=8,
                radius=[20],
                size_hint=(1, None),
                height=130,
                md_bg_color=(0.05, 0.10, 0.12, 0.88)
            )

            card.add_widget(MDLabel(
                text=alert["title"],
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 0.45, 0.45, 1)
            ))

            card.add_widget(MDLabel(
                text=f"Severity: {alert['severity']}",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            ))

            card.add_widget(MDLabel(
                text=f"Category: {alert['category']}",
                theme_text_color="Custom",
                text_color=(0.8, 1, 1, 1)
            ))

            card.add_widget(MDLabel(
                text=f"Detected: {alert['time']}",
                theme_text_color="Custom",
                text_color=(0.8, 0.8, 0.8, 1)
            ))

            self.content.add_widget(card)

    # =========================================
    # BACKGROUND UPDATE
    # =========================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
