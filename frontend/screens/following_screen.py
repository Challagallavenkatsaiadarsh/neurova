import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView

from kivy.graphics import Rectangle
from kivy.metrics import dp


class FollowingScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_user_id = ""
        self.profile_user_id = ""

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
        # ROOT
        # =========================
        scroll = MDScrollView()

        self.root = MDBoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )
        self.root.bind(minimum_height=self.root.setter("height"))

        # =========================
        # TAB (ALL / MUTUAL)
        # =========================
        tab_box = MDBoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )

        self.btn_all = MDRaisedButton(
            text="ALL",
            on_release=lambda x: self.load_following("all")
        )

        self.btn_mutual = MDRaisedButton(
            text="MUTUAL",
            on_release=lambda x: self.load_following("mutual")
        )

        tab_box.add_widget(self.btn_all)
        tab_box.add_widget(self.btn_mutual)

        # =========================
        # LIST
        # =========================
        self.list_area = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=6
        )
        self.list_area.bind(minimum_height=self.list_area.setter("height"))

        # =========================
        # BUILD
        # =========================
        self.root.add_widget(tab_box)
        self.root.add_widget(self.list_area)

        scroll.add_widget(self.root)
        self.add_widget(scroll)

        self.load_following("all")

    # =========================
    # UPDATE BACKGROUND
    # =========================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # =========================
    # LOAD FOLLOWING
    # =========================
    def load_following(self, mode):

        self.list_area.clear_widgets()

        if mode == "all":
            users = ["Following A", "Following B", "Following C"]
        else:
            users = ["Mutual Following X"]

        for u in users:
            card = MDCard(
                size_hint=(1, None),
                height=60,
                padding=10,
                radius=[12],
                md_bg_color=(0.05, 0.08, 0.12, 0.75)
            )

            card.add_widget(
                MDLabel(
                    text=u,
                    halign="left",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            )

            self.list_area.add_widget(card)
