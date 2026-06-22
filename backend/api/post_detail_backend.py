from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
import requests


class PostDetailScreen(MDScreen):
    current_post_id = None
    BASE_URL = "http://127.0.0.1:5000/api"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = MDBoxLayout(orientation="vertical")
        self.scroll = MDScrollView()

        self.content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
            padding=dp(12),
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        self.scroll.add_widget(self.content)
        self.root_layout.add_widget(self.scroll)
        self.add_widget(self.root_layout)

        self.editing_comment_id = None
        self.comment_input = None
        self.send_btn = None
        self.menu = None

    # -------------------------
    def on_pre_enter(self):
        if self.current_post_id:
            self.load_post(self.current_post_id)

    # -------------------------
    def load_post(self, post_id):
        try:
            res = requests.get(f"{self.BASE_URL}/feed", timeout=10)
            posts = res.json().get("posts", [])

            self.current_post = next(
                (p for p in posts if str(p.get("id")) == str(post_id)),
                None
            )

            if self.current_post:
                self.render_post()

        except Exception as e:
            print("LOAD ERROR:", e)

    # -------------------------
    def render_post(self):
        self.content.clear_widgets()
        post = self.current_post

        self.current_post_id = post["id"]

        self.content.add_widget(
            MDIconButton(icon="arrow-left", on_release=lambda x: self.go_back())
        )

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(15),
            spacing=dp(10),
            radius=[20],
            md_bg_color=(0.1, 0.1, 0.1, 1),
        )

        # username
        card.add_widget(
            MDLabel(
                text=f"@{post.get('username','user')}",
                size_hint_y=None,
                height=dp(25),
            )
        )

        # text
        if post.get("text"):
            card.add_widget(
                MDLabel(
                    text=post["text"],
                    size_hint_y=None,
                    height=dp(60),
                )
            )

        # ✅ IMAGE FIX (IMPORTANT)
        if post.get("image"):
            img_url = post.get("image")
            if img_url.strip() != "":
                card.add_widget(
                    AsyncImage(
                        source=img_url,
                        size_hint_y=None,
                        height=dp(250),
                        allow_stretch=True,
                        keep_ratio=True,
                    )
                )

        self.content.add_widget(card)

        # input
        input_box = MDBoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))

        self.comment_input = MDTextField(hint_text="Write comment...")

        self.send_btn = MDRoundFlatButton(
            text="Reply",
            on_release=lambda x: self.send_comment(self.current_post_id),
        )

        input_box.add_widget(self.comment_input)
        input_box.add_widget(self.send_btn)

        self.content.add_widget(input_box)

        # comments list
        self.reply_list = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        self.reply_list.bind(minimum_height=self.reply_list.setter("height"))

        self.content.add_widget(self.reply_list)

        self.render_comments(post.get("comments", []))

    # -------------------------
    def render_comments(self, comments):
        self.reply_list.clear_widgets()

        for c in comments:
            cid = c.get("id")
            text = c.get("text", "")

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10),
            )

            row.add_widget(MDLabel(text=text))

            menu_btn = MDIconButton(icon="dots-vertical")

            menu_btn.bind(
                on_release=lambda x, cid=cid, text=text: self.open_comment_menu(x, cid, text)
            )

            row.add_widget(menu_btn)
            self.reply_list.add_widget(row)

    # -------------------------
    def open_comment_menu(self, button, cid, text):
        if self.menu:
            self.menu.dismiss()

        items = [
            {
                "text": "Edit",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=None: self.edit_comment(cid, text),
            },
            {
                "text": "Delete",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=None: self.delete_comment(cid),
            },
        ]

        self.menu = MDDropdownMenu(
            caller=button,
            items=items,
            width_mult=3,
        )
        self.menu.open()

    # -------------------------
    def edit_comment(self, cid, text):
        self.editing_comment_id = cid
        self.comment_input.text = text
        self.send_btn.text = "Update"

        if self.menu:
            self.menu.dismiss()

    # -------------------------
    # DELETE (MATCH BACKEND EXACTLY)
    # -------------------------
    def delete_comment(self, cid):
        if self.menu:
            self.menu.dismiss()

        try:
            url = f"{self.BASE_URL}/feed/comment/delete/{self.current_post_id}/{cid}"
            resp = requests.delete(url)

            print("DELETE:", resp.status_code, resp.text)

            self.load_post(self.current_post_id)

        except Exception as e:
            print("DELETE ERROR:", e)

    # -------------------------
    # SEND / UPDATE (FIXED ROUTES)
    # -------------------------
    def send_comment(self, post_id):
        text = self.comment_input.text.strip()
        if not text:
            return

        try:
            # UPDATE COMMENT (IMPORTANT FIX)
            if self.editing_comment_id:
                url = f"{self.BASE_URL}/feed/comment/edit/{self.current_post_id}/{self.editing_comment_id}"
                resp = requests.put(url, json={"text": text})

                print("UPDATE:", resp.status_code, resp.text)

                self.editing_comment_id = None
                self.send_btn.text = "Reply"

            # CREATE COMMENT
            else:
                url = f"{self.BASE_URL}/feed/comment/{post_id}"
                resp = requests.post(
                    url,
                    json={"text": text, "username": "user"},
                )

                print("POST:", resp.status_code, resp.text)

            self.comment_input.text = ""
            self.load_post(self.current_post_id)

        except Exception as e:
            print("ERROR:", e)

    # -------------------------
    def go_back(self):
        self.manager.current = "feed"
