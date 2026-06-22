import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton

from kivy.graphics import Rectangle


class FollowersScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # =========================
        # BACKGROUND IMAGE
        # =========================
        with self.canvas.before:
            self.bg = Rectangle(
                source=r"C:\Users\Admin\Downloads\WhatsApp Image 2026-06-20 at 8.42.46 AM.jpeg",
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)

        # =========================
        # STATE
        # =========================
        self.profile_user_id = ""
        self.current_mode = "all"

        # =========================
        # ROOT LAYOUT
        # =========================
        self.root = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        # =========================
        # TOP TAB BUTTONS
        # =========================
        tab_box = MDBoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )

        self.all_btn = MDRaisedButton(
            text="ALL",
            on_release=lambda x: self.load_followers("all")
        )

        self.mutual_btn = MDRaisedButton(
            text="MUTUAL",
            on_release=lambda x: self.load_followers("mutual")
        )

        tab_box.add_widget(self.all_btn)
        tab_box.add_widget(self.mutual_btn)

        # =========================
        # SCROLL AREA
        # =========================
        self.list_area = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8
        )
        self.list_area.bind(
            minimum_height=self.list_area.setter("height")
        )

        scroll = MDScrollView()
        scroll.add_widget(self.list_area)

        # =========================
        # BUILD UI
        # =========================
        self.root.add_widget(tab_box)
        self.root.add_widget(scroll)

        self.add_widget(self.root)

    # =========================
    # UPDATE BACKGROUND
    # =========================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # =========================
    # SET USER
    # =========================
    def set_user(self, user_id):
        self.profile_user_id = user_id
        self.load_followers("all")

    # =========================
    # LOAD FOLLOWERS
    # =========================
    def load_followers(self, mode):

        self.current_mode = mode
        self.list_area.clear_widgets()

        try:
            res = requests.get(
                f"http://127.0.0.1:5000/api/user/followers/{self.profile_user_id}"
            )

            data = res.json()

            if data.get("success"):
                followers = data.get("followers", [])
                mutual = data.get("mutual", [])

                users = followers if mode == "all" else mutual
            else:
                users = self.demo_data(mode)

        except Exception as e:
            print("Followers load error:", e)
            users = self.demo_data(mode)

        # =========================
        # RENDER USERS
        # =========================
        for user in users:
            self.list_area.add_widget(
                self.create_card(user)
            )

    # =========================
    # DEMO DATA
    # =========================
    def demo_data(self, mode):

        if mode == "all":
            return [
                "Follower A",
                "Follower B",
                "Follower C",
                "Follower D"
            ]

        return [
            "Mutual User X",
            "Mutual User Y"
        ]

    # =========================
    # USER CARD UI
    # =========================
    def create_card(self, username):

        card = MDCard(
            size_hint=(1, None),
            height=60,
            padding=10,
            radius=[12],
            md_bg_color=(0.05, 0.08, 0.12, 0.75)
        )

        card.add_widget(
            MDLabel(
                text=username,
                halign="left",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            )
        )

        return card
