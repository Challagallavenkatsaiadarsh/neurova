# =========================================
# FILE: frontend/screens/signup_screen.py
# =========================================

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


class SignupScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg = None

        # =========================================
        # BACKGROUND IMAGE
        # =========================================
        with self.canvas.before:
            self.bg = Rectangle(
                source=r"C:\Users\Admin\Documents\neurova\frontend\assets\images\neurova_signup_bg.png",
                pos=self.pos,
                size=self.size
            )

        self.bind(size=self.update_bg, pos=self.update_bg)

        # =========================================
        # MAIN LAYOUT
        # =========================================
        main_layout = BoxLayout(
            orientation="vertical",
            padding=[25, 30, 25, 30],
            spacing=15
        )

        main_layout.add_widget(
            Widget(size_hint_y=None, height=40)
        )

        # =========================================
        # TITLE
        # =========================================
        title = MDLabel(
            text="Create Account",
            halign="center",
            font_style="H3",
            bold=True,
            theme_text_color="Custom",
            text_color=(0, 1, 1, 1),
            size_hint_y=None,
            height=70
        )

        # =========================================
        # SUBTITLE
        # =========================================
        subtitle = MDLabel(
            text="Join the future of AI social networking",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.92),
            size_hint_y=None,
            height=40
        )

        # =========================================
        # SIGNUP CARD
        # =========================================
        signup_card = MDCard(
            orientation="vertical",
            padding=35,
            spacing=25,
            size_hint=(0.78, None),
            height=430,
            pos_hint={"center_x": 0.5},
            radius=[35, 35, 35, 35],
            elevation=0,
            md_bg_color=(0.0, 0.0, 0.0, 0.28),
            line_color=(0, 1, 1, 0.35),
            line_width=1.3
        )

        # =========================================
        # USERNAME
        # =========================================
        self.username = MDTextField(
            hint_text="Username",
            mode="round",
            icon_right="account"
        )

        # =========================================
        # EMAIL
        # =========================================
        self.email = MDTextField(
            hint_text="Email",
            mode="round",
            icon_right="email"
        )

        # =========================================
        # PASSWORD
        # =========================================
        self.password = MDTextField(
            hint_text="Password",
            password=True,
            mode="round",
            icon_right="lock"
        )

        # =========================================
        # SIGNUP BUTTON
        # =========================================
        signup_btn = MDRoundFlatButton(
            text="SIGN UP",
            pos_hint={"center_x": 0.5},
            text_color=(0, 1, 1, 1),
            line_color=(0, 1, 1, 1),
            on_release=self.signup
        )

        # =========================================
        # BACK BUTTON
        # =========================================
        back_btn = MDRoundFlatButton(
            text="BACK TO LOGIN",
            pos_hint={"center_x": 0.5},
            text_color=(0.7, 0.5, 1, 1),
            line_color=(0, 0.7, 1, 1),
            on_release=self.goto_login
        )

        # =========================================
        # ADD WIDGETS
        # =========================================
        signup_card.add_widget(self.username)
        signup_card.add_widget(self.email)
        signup_card.add_widget(self.password)
        signup_card.add_widget(
            Widget(size_hint_y=None, height=10)
        )
        signup_card.add_widget(signup_btn)
        signup_card.add_widget(back_btn)

        # =========================================
        # ADD TO MAIN LAYOUT
        # =========================================
        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(
            Widget(size_hint_y=None, height=20)
        )
        main_layout.add_widget(signup_card)

        self.add_widget(main_layout)

    # =========================================
    # BACKGROUND RESIZE
    # =========================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # =========================================
    # SIGNUP
    # =========================================
    def signup(self, instance):

        username = self.username.text.strip()
        email = self.email.text.strip().lower()
        password = self.password.text.strip()

        if not username or not email or not password:
            MDDialog(
                title="Signup Failed",
                text="Please fill all fields"
            ).open()
            return

        try:

            response = requests.post(
                "http://127.0.0.1:5000/api/auth/signup",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                },
                timeout=15
            )

            data = response.json()

            if response.status_code in [200, 201] and data.get("success"):

                MDDialog(
                    title="Success",
                    text="Account created successfully"
                ).open()

                self.username.text = ""
                self.email.text = ""
                self.password.text = ""

                self.manager.current = "login"

            else:

                MDDialog(
                    title="Signup Failed",
                    text=data.get(
                        "message",
                        "Unable to create account"
                    )
                ).open()

        except Exception as e:

            MDDialog(
                title="Network Error",
                text=str(e)
            ).open()

    # =========================================
    # BACK TO LOGIN
    # =========================================
    def goto_login(self, instance):
        self.manager.current = "login"
