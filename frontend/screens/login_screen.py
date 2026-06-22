# =========================================
# FILE: frontend/screens/login_screen.py (CLEAN FIXED)
# =========================================

import os
import sys
import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.dialog import MDDialog

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle


class LoginScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg = None
        self.otp_boxes = []

        self.temp_email = None
        self.temp_password = None
        self.social_provider = None

        # =========================
        # BACKGROUND
        # =========================
        with self.canvas.before:
            self.bg = Rectangle(
                source=r"C:\Users\Admin\Documents\neurova\frontend\assets\images\neurova_login_bg.png",
                pos=self.pos,
                size=self.size
            )

        self.bind(size=self.update_bg, pos=self.update_bg)

        # =========================
        # UI
        # =========================
        main_layout = BoxLayout(
            orientation="vertical",
            padding=[25, 35, 25, 35],
            spacing=15
        )

        main_layout.add_widget(Widget(size_hint_y=None, height=70))

        title = MDLabel(
            text="NEUROVA",
            halign="center",
            font_style="H1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.0, 1.0, 1.0, 1)
        )

        subtitle = MDLabel(
            text="AI Social Intelligence + Cyber Security",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.95)
        )

        login_card = MDCard(
            orientation="vertical",
            padding=30,
            spacing=20,
            size_hint=(0.72, None),
            height=350,
            pos_hint={"center_x": 0.5},
            md_bg_color=(0, 0, 0, 0.35)
        )

        self.email = MDTextField(
            hint_text="Email",
            mode="round",
            icon_right="email"
        )

        self.password = MDTextField(
            hint_text="Password",
            password=True,
            mode="round",
            icon_right="lock"
        )

        # =========================
        # BUTTONS
        # =========================
        login_btn = MDRoundFlatButton(
            text="LOGIN",
            pos_hint={"center_x": 0.5},
            on_release=self.login
        )

        signup_btn = MDRoundFlatButton(
            text="CREATE ACCOUNT",
            pos_hint={"center_x": 0.5},
            on_release=self.goto_signup
        )

        self.security_label = MDLabel(
            text="🛡 Safe | Score: 100",
            halign="center"
        )

        login_card.add_widget(self.email)
        login_card.add_widget(self.password)
        login_card.add_widget(login_btn)
        login_card.add_widget(signup_btn)
        login_card.add_widget(self.security_label)

        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(Widget(size_hint_y=None, height=25))
        main_layout.add_widget(login_card)

        self.add_widget(main_layout)

    # =========================================
    # LOGIN
    # =========================================
    def login(self, instance):
        self.temp_email = self.email.text.strip()
        self.temp_password = self.password.text.strip()

        if not self.temp_email or not self.temp_password:
            MDDialog(title="Error", text="Enter email & password").open()
            return

        self.request_login()

    # =========================================
    # REQUEST LOGIN
    # =========================================
    def request_login(self):

        try:
            url = "http://127.0.0.1:5000/auth/login"

            response = requests.post(
                url,
                json={
                    "email": self.temp_email,
                    "password": self.temp_password
                },
                timeout=10
            )

            data = response.json()

            if response.status_code == 202 and data.get("mfa_required"):
                self.show_otp_dialog()
                return

            if response.status_code == 200 and data.get("success"):

                user = data.get("user", {})

                self.security_label.text = (
                    f"🛡 {user.get('security_status', 'Safe')} | "
                    f"Score: {user.get('cyber_score', 100)}"
                )

                # STORE SESSION
                self.manager.user_id = user.get("id")
                self.manager.username = user.get("username")
                self.manager.email = user.get("email")

                # ONBOARDING CHECK
                if data.get("needs_onboarding", False):
                    self.manager.current = "onboarding"
                else:
                    self.manager.current = "feed"

                return

            MDDialog(
                title="Login Failed",
                text=data.get("message", "Invalid credentials")
            ).open()

        except Exception as e:
            MDDialog(
                title="Error",
                text=str(e)
            ).open()

    # =========================================
    # OTP DIALOG
    # =========================================
    def show_otp_dialog(self):
        otp_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=70)

        self.otp_boxes = []

        for i in range(4):
            box = MDTextField(
                hint_text="•",
                max_text_length=1,
                mode="rectangle",
                size_hint_x=None,
                width=60,
                halign="center"
            )
            self.otp_boxes.append(box)
            otp_layout.add_widget(box)

        self.otp_dialog = MDDialog(
            title="Enter OTP",
            type="custom",
            content_cls=otp_layout,
            buttons=[
                MDRoundFlatButton(text="VERIFY", on_release=self.verify_otp)
            ]
        )

        self.otp_dialog.open()

    # =========================================
    # VERIFY OTP
    # =========================================
    def verify_otp(self, instance):

        otp = "".join([b.text.strip() for b in self.otp_boxes])

        try:
            url = "http://127.0.0.1:5000/api/auth/login"

            response = requests.post(
                url,
                json={
                    "email": self.temp_email,
                    "password": self.temp_password,
                    "otp": otp
                },
                timeout=10
            )

            data = response.json()

            if response.status_code == 200 and data.get("success"):

                self.otp_dialog.dismiss()

                user = data.get("user", {})

                self.security_label.text = (
                    f"🛡 {user.get('security_status', 'Safe')} | "
                    f"Score: {user.get('cyber_score', 100)}"
                )

                self.manager.current = "feed"
            else:
                MDDialog(title="OTP Failed", text=data.get("message")).open()

        except Exception as e:
            MDDialog(title="Error", text=str(e)).open()

    # =========================================
    # BACKGROUND UPDATE
    # =========================================
    def update_bg(self, *args):
        if self.bg:
            self.bg.pos = self.pos
            self.bg.size = self.size

    # =========================================
    # GO TO SIGNUP
    # =========================================
    def goto_signup(self, instance):
        self.manager.current = "signup"
