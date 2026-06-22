from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.image import Image
import os


class SpaceCommentsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.messages = []
        self.reactions = []

        root = MDBoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )

        # ================= HEADER =================
        header = MDCard(
            adaptive_height=True,
            padding=15,
            radius=[20],
            md_bg_color=(0.05, 0.07, 0.1, 0.95)
        )

        self.title = MDLabel(
            text="💬 SPACE COMMENTS",
            halign="center",
            bold=True
        )

        header.add_widget(self.title)
        root.add_widget(header)

        # ================= COMMENTS =================
        self.comment_list = MDBoxLayout(
            orientation="vertical",
            spacing=8,
            adaptive_height=True
        )

        scroll = MDScrollView()
        scroll.add_widget(self.comment_list)

        root.add_widget(scroll)

        # ================= INPUT =================
        input_box = MDBoxLayout(
            adaptive_height=True,
            spacing=8
        )

        from kivymd.uix.textfield import MDTextField

        self.input = MDTextField(
            hint_text="Write a comment..."
        )

        send_btn = MDRaisedButton(
            text="Send",
            on_release=self.send_comment
        )

        input_box.add_widget(self.input)
        input_box.add_widget(send_btn)

        root.add_widget(input_box)

        # ================= REACTIONS =================
        self.reaction_bar = MDBoxLayout(
            adaptive_height=True,
            spacing=5
        )

        root.add_widget(self.reaction_bar)

        self.add_widget(root)

        # ================= AUTO UPDATE =================
        Clock.schedule_interval(self.refresh, 1)

    # =========================================
    # SEND COMMENT
    # =========================================
    def send_comment(self, *args):

        text = self.input.text.strip()

        if not text:
            return

        app = App.get_running_app()

        if hasattr(app, "selected_space"):
            username = app.selected_space.get("user", "User")
        else:
            username = "User"

        msg = f"{username}: {text}"

        self.messages.append(msg)

        self.input.text = ""

    # =========================================
    # REFRESH UI
    # =========================================
    def refresh(self, dt):

        self.comment_list.clear_widgets()
        self.reaction_bar.clear_widgets()

        # ================= COMMENTS =================
        for msg in self.messages[-50:]:

            card = MDCard(
                adaptive_height=True,
                padding=10,
                radius=[15],
                md_bg_color=(0.1, 0.1, 0.12, 0.95)
            )

            card.add_widget(
                MDLabel(text=msg, adaptive_height=True)
            )

            self.comment_list.add_widget(card)

        # ================= REACTIONS =================
        for r in self.reactions[-10:]:

            self.reaction_bar.add_widget(
                Image(
                    source=r,
                    size_hint=(None, None),
                    size=(dp(30), dp(30))
                )
            )

    # =========================================
    # ADD FROM OUTSIDE (LIVE DISCUSSION)
    # =========================================
    def add_comment(self, msg):
        self.messages.append(msg)

    def add_reaction(self, img_path):
        self.reactions.append(img_path)
