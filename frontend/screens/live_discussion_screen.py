from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.metrics import dp

import threading
import asyncio
import os
import requests
import time

from livekit import rtc
from backend.core.activity_store import add_activity


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")


class LiveDiscussionScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ================= STATE =================
        self.room = None
        self._token_data = {}

        self.local_username = "You"

        # 🚨 SAFE ROOM ID
        self._fallback_room_id = f"space_{int(time.time() * 1000)}"
        self._token_data["room"] = self._fallback_room_id

        # ================= ROLES =================
        self.roles = {}
        self.hand_raise = set()

        self.host = "Host"
        self.cohosts = set()
        self.speakers = set()
        self.listeners = set()

        # ================= DATA =================
        self.messages = []
        self.comments_persisted = []
        self.reactions = []

        # ================= ENGAGEMENT =================
        self.likes = 0
        self.bookmarks = 0
        self.shares = 0

        self.space_already_ended = False

        # ================= BACKGROUND =================
        with self.canvas.before:
            self.bg = Rectangle(
                source=os.path.join(IMAGE_DIR, "spaces_bg.jpg"),
                pos=self.pos,
                size=self.size
            )
            Color(0, 0, 0, 0.72)
            self.overlay = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= UI =================
        root = MDBoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        header = MDCard(adaptive_height=True, padding=15, radius=[25])
        header.add_widget(MDLabel(text="🎤 LIVE SPACE", halign="center"))
        root.add_widget(header)

        main = MDBoxLayout(orientation="horizontal", spacing=dp(10))

        users = MDCard(size_hint_x=0.7, padding=10, radius=[25])
        self.user_grid = MDGridLayout(cols=4, spacing=dp(10), adaptive_height=True)

        scroll = MDScrollView()
        scroll.add_widget(self.user_grid)
        users.add_widget(scroll)

        main.add_widget(users)
        main.add_widget(Widget())
        root.add_widget(main)

        self.reaction_bar = MDBoxLayout(adaptive_height=True, spacing=5)
        root.add_widget(self.reaction_bar)

        controls = MDBoxLayout(adaptive_height=True, spacing=10)
        controls.add_widget(MDRaisedButton(text="🎤 TALK"))
        controls.add_widget(MDRaisedButton(text="✋ REQUEST", on_release=self.raise_hand))
        controls.add_widget(MDRaisedButton(text="👑 COHOST", on_release=self.make_cohost))
        controls.add_widget(MDRaisedButton(text="🎙 SPEAKER", on_release=self.make_speaker))
        controls.add_widget(MDRaisedButton(text="🚪 END SPACE", on_release=self.end_space))
        controls.add_widget(MDIconButton(icon="comment", on_release=self.open_comments))

        root.add_widget(controls)
        self.add_widget(root)

        # ================= LOOP =================
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()
        Clock.schedule_interval(self.refresh_ui, 1)

    # =========================================================
    # SAFE ROOM ID
    # =========================================================
    def _get_room_id(self):
        if not isinstance(self._token_data, dict):
            self._token_data = {}

        rid = (
            self._token_data.get("room")
            or self._token_data.get("room_id")
            or self._token_data.get("id")
            or self._fallback_room_id
        )

        rid = str(rid).strip()

        if not rid or rid.lower() == "none":
            rid = self._fallback_room_id

        self._token_data["room"] = rid
        return rid

    # =========================================================
    # 🔥 POST SANITIZER (IMPORTANT FIX)
    # =========================================================
    def _sanitize_post(self, post):
        if not isinstance(post, dict):
            post = {}

        room_id = self._get_room_id()

        return {
            "id": str(post.get("id") or room_id),
            "post_id": str(post.get("post_id") or room_id),
            "username": post.get("username", self.host),
            "text": post.get("text", ""),
            "image": post.get("image", ""),
            "type": post.get("type", "space"),
            "source": post.get("source", "space"),
            "space_id": str(post.get("space_id") or room_id),
        }

    # =========================================================
    # TRACKING SYSTEM (HARD GUARANTEE FIX)
    # =========================================================
    def _safe_activity(self, action, username, payload):
        room_id = self._get_room_id()

        # ALWAYS CLEAN FIRST
        payload = self._sanitize_post(payload)

        # FORCE OVERRIDE (NO WAY TO FAIL)
        payload["post_id"] = str(room_id)
        payload["id"] = str(room_id)
        payload["space_id"] = str(room_id)

        add_activity(action, username, payload)

    def track_like(self):
        self.likes += 1
        self.reactions.append("❤️")

        self._safe_activity("likes", self.local_username, {
            "username": self.host,
            "text": "Live Space Like",
            "source": "space"
        })

    def track_bookmark(self):
        self.bookmarks += 1
        self.reactions.append("🔖")

        self._safe_activity("bookmarks", self.local_username, {
            "username": self.host,
            "text": "Live Space Bookmark",
            "source": "space"
        })

    def track_share(self):
        self.shares += 1
        self.reactions.append("🔁")

        self._safe_activity("shares", self.local_username, {
            "username": self.host,
            "text": "Live Space Share",
            "source": "space"
        })

    def track_comment(self, text):
        self.reactions.append("💬")

        self._safe_activity("replies", self.local_username, {
            "username": self.host,
            "text": text,
            "source": "space"
        })

    # =========================================================
    # SPACE DATA
    # =========================================================
    def set_space_data(self, data):
        if not data:
            return

        self._token_data = data

        room_id = (
            data.get("room")
            or data.get("room_id")
            or data.get("id")
            or self._fallback_room_id
        )

        self._token_data["room"] = str(room_id)

        self.local_username = data.get("user", "You")
        self.host = data.get("host", "Host")

        self.roles.clear()
        self.roles[self.host] = "host"

        for p in data.get("participants", []):
            if p != self.host:
                self.roles[p] = "listener"

        print("✅ SPACE LOADED:", self._token_data["room"])

    # =========================================================
    # ROLE SYSTEM
    # =========================================================
    def raise_hand(self, *args):
        self.hand_raise.add(self.local_username)
        self.roles[self.local_username] = "hand raised"
        self.track_like()

    def make_speaker(self, *args):
        pass

    def make_cohost(self, *args):
        pass

    # =========================================================
    # COMMENTS
    # =========================================================
    def open_comments(self, *args):
        box = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        scroll = MDScrollView()

        list_box = MDBoxLayout(orientation="vertical", spacing=8, adaptive_height=True)

        for msg in (self.comments_persisted + self.messages):
            card = MDCard(adaptive_height=True, padding=10, radius=[15])
            card.add_widget(MDLabel(text=msg))
            list_box.add_widget(card)

        scroll.add_widget(list_box)
        box.add_widget(scroll)

        self.dialog = MDDialog(
            title="💬 Comments",
            type="custom",
            content_cls=box
        )
        self.dialog.open()

    def send_message(self, text):
        msg = f"{self.local_username}: {text}"
        self.messages.append(msg)
        self.track_comment(msg)

    # =========================================================
    # END SPACE
    # =========================================================
    def end_space(self, *args):
        if self.space_already_ended:
            return

        self.space_already_ended = True

        room_id = self._get_room_id()

        try:
            requests.delete(
                f"http://127.0.0.1:5000/spaces/{room_id}",
                timeout=5
            )
        except Exception as e:
            print("Backend delete error:", e)

        post_data = {
            "id": room_id,
            "post_id": room_id,
            "username": f"🎤 LIVE SPACE ({self.host})",
            "text": f"Live Space Ended\n❤️ {self.likes} 🔖 {self.bookmarks} 🔁 {self.shares}",
            "image": "",
            "type": "space",
            "source": "space",
            "space_id": room_id,
            "host": self.host
        }

        feed_screen = self.manager.get_screen("feed")

        if hasattr(feed_screen, "set_space_data"):
            feed_screen.set_space_data(post_data)

        if hasattr(feed_screen, "load_posts"):
            feed_screen.load_posts()

        self.manager.current = "feed"

    # =========================================================
    # UI
    # =========================================================
    def refresh_ui(self, dt):
        self.user_grid.clear_widgets()

        for user, role in self.roles.items():
            card = MDCard(adaptive_height=True, padding=10, radius=[18])
            card.add_widget(MDLabel(text=f"{user}\n{role}", halign="center"))
            self.user_grid.add_widget(card)

        self.reaction_bar.clear_widgets()
        for r in self.reactions[-10:]:
            self.reaction_bar.add_widget(MDLabel(text=r))

    # =========================================================
    # LOOP
    # =========================================================
    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # =========================================================
    # BACKGROUND
    # =========================================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.overlay.pos = self.pos
        self.overlay.size = self.size
