# =========================================
# FILE: frontend/screens/security_center.py
# =========================================

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton


class SecurityCenterScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = MDLabel(
            text="🛡 Neurova Security Center",
            halign="center",
            font_style="H5"
        )

        root.add_widget(title)

        features = [
            "🔗 Safe Link Sandbox",
            "🧠 AI Scam Detection",
            "📱 Device Fingerprinting",
            "🚨 Threat Alerts",
            "🛡 Cyber Shield Score",
            "🔐 Account Takeover Protection"
        ]

        for item in features:

            card = MDCard(
                orientation="vertical",
                padding=15,
                radius=[20],
                size_hint=(1, None),
                height=80,
                md_bg_color=(0.05, 0.08, 0.09, 1)
            )

            card.add_widget(
                MDLabel(
                    text=item,
                    halign="left"
                )
            )

            root.add_widget(card)

        open_score = MDRaisedButton(
            text="OPEN CYBER SCORE",
            pos_hint={"center_x": 0.5},
            on_release=self.goto_score
        )

        root.add_widget(open_score)

        self.add_widget(root)

    def goto_score(self, instance):

        self.manager.current = "cyber_score"
