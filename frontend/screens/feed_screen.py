from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.graphics import Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.uix.menu import MDDropdownMenu
import requests
import socket

from backend.core.activity_store import (
    add_activity,
    remove_activity,
    get_activity
)

# =========================================================
# 🌍 CROSS-PLATFORM BASE URL CONFIG (PRODUCTION + DEV)
# =========================================================

import os
from kivy.utils import platform

# ================= PRODUCTION API =================
BASE_URL_PROD = "https://novix.com"   # 🔥 MUST BE HTTPS in production

# ================= LOCAL DEV =================
BASE_URL_DEV = "http://127.0.0.1:5000"

# ================= FINAL SWITCH =================
if platform in ("android", "ios"):
    # Mobile always uses production domain
    BASE_URL = os.getenv("NOVIX_API_URL", BASE_URL_PROD)

else:
    # Desktop / local testing only
    BASE_URL = BASE_URL_DEV
    
class FeedScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ================= API =================
        self.API_URL = f"{BASE_URL}/feed"
        self.USER_API = f"{BASE_URL}/user"
        self.POST_API = f"{BASE_URL}/post"

        # ================= STATE =================
        self.post_state = {}
        self.user_id = "current_user"
        self.space_posts = []

        # ================= BACKGROUND =================
        with self.canvas.before:
            self.bg = Rectangle(
                source="assets/images/bg3.jpg",
                pos=self.pos,
                size=self.size
            )
        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= ROOT =================
        self.root_layout = BoxLayout(orientation="horizontal")

        # ================= SIDEBAR =================
        self.sidebar_scroll = MDScrollView(
            size_hint=(0.14, 1),
            bar_width=0,
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.sidebar = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(22),
            padding=[dp(10), dp(30), dp(10), dp(30)],
            adaptive_height=True,
            md_bg_color=(0.02, 0.08, 0.06, 1)
        )
        self.sidebar.bind(minimum_height=self.sidebar.setter("height"))

        self.sidebar.add_widget(
            MDLabel(
                text="N",
                halign="center",
                size_hint_y=None,
                height=dp(80),
                font_style="H3",
                theme_text_color="Custom",
                text_color=(0.3, 0.95, 0.75, 1)
            )
        )

        nav_items = [
            ("home", self.goto_feed),
            ("magnify", self.goto_search),
            ("robot", self.goto_ai),
            ("bell", self.goto_notifications),
            ("microphone", self.goto_spaces),
            ("plus-box", self.goto_create_space),
            ("shield-check", self.goto_cyber_score),
            ("web", self.goto_safe_browser),
            ("alert", self.goto_threat_alert),
            ("plus-circle", self.goto_create_post),
            ("account", self.goto_profile),
            ("cog", self.goto_settings),
        ]

        for icon, action in nav_items:
            self.sidebar.add_widget(
                MDIconButton(
                    icon=icon,
                    icon_size="28sp",
                    size_hint_y=None,
                    height=dp(55),
                    theme_icon_color="Custom",
                    icon_color=(0.7, 0.7, 0.7, 1),
                    on_release=action
                )
            )

        self.sidebar.add_widget(Widget(size_hint_y=None, height=dp(25)))

        self.sidebar.add_widget(
            MDRoundFlatButton(
                text="+ POST",
                size_hint_y=None,
                height=dp(50),
                md_bg_color=(0.1, 0.85, 0.65, 1),
                text_color=(0, 0, 0, 1),
                on_release=self.goto_create_post
            )
        )

        self.sidebar_scroll.add_widget(self.sidebar)

        # ================= FEED =================
        self.scroll = MDScrollView()
        self.feed_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            adaptive_height=True,
            padding=[dp(10), dp(10), dp(10), dp(120)]
        )

        self.scroll.add_widget(self.feed_layout)

        self.root_layout.add_widget(self.sidebar_scroll)
        self.root_layout.add_widget(self.scroll)
        self.add_widget(self.root_layout)

        self.load_posts()
        Window.bind(size=self.on_size)

    # =========================================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def load_posts(self):
        try:
            res = requests.get(self.API_URL, timeout=5)
            if res.status_code != 200:
                print("API Error:", res.text)
                return

            posts = res.json().get("posts", [])
            all_posts = self.space_posts + posts
            self.render_posts(all_posts)

        except Exception as e:
            print("Load error:", e)

    def set_space_data(self, data):
        if not data:
            return

        room_id = data.get("room_id") or data.get("room") or data.get("id")
        if not room_id:
            return

        space_post = {
            "id": room_id,
            "post_id": room_id,
            "username": f"🎤 LIVE SPACE ({data.get('host', 'Host')})",
            "text": f"Participants: {len(data.get('participants', []))}\n❤️ {data.get('likes', 0)} 🔖 {data.get('bookmarks', 0)} 🔁 {data.get('shares', 0)}",
            "image": "",
            "type": "space",
            "source": "space",
            "space_id": room_id
        }

        self.space_posts.insert(0, space_post)
        self.load_posts()

    def render_posts(self, posts):
        self.feed_layout.clear_widgets()
        for post in posts:
            self.feed_layout.add_widget(self.create_post(post))

    def create_post(self, post):

        post_id = post.get("id") or "unknown"

        state = self.post_state.setdefault(post_id, {
            "liked": False,
            "bookmarked": False,
            "reposted": False,
            "likes": 0,
            "bookmarks": 0,
            "reposts": 0,
            "replies": 0
        })

        card = MDCard(
            orientation="vertical",
            size_hint=(0.95, None),
            adaptive_height=True,
            pos_hint={"center_x": 0.5},
            padding=dp(12),
            spacing=dp(10),
            radius=[24]
        )

        # ================= HEADER =================
        header = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        header.add_widget(MDLabel(text=f"@{post.get('username','user')}"))

        if post.get("type") == "space":
            header.add_widget(MDLabel(text="🔴 LIVE", halign="right"))

        menu_btn = MDIconButton(icon="dots-vertical")
        menu_btn.bind(on_release=lambda x, p=post: self.open_post_menu(x, p))
        header.add_widget(menu_btn)

        card.add_widget(header)

        # ================= CONTENT =================
        if post.get("image"):
            card.add_widget(AsyncImage(source=post["image"], size_hint_y=None, height=dp(220)))

        if post.get("text"):
            card.add_widget(MDLabel(text=post["text"], adaptive_height=True))

        # ================= ACTION BAR =================
        action_bar = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        # LIKE
        like_btn = MDIconButton(icon="heart-outline")
        like_lbl = MDLabel(text=str(state["likes"]), size_hint_x=None, width=dp(25))
        like_btn.bind(on_release=lambda x, p=post: self.toggle_like(post_id, like_btn, like_lbl, p))
        action_bar.add_widget(like_btn)
        action_bar.add_widget(like_lbl)

        # COMMENT (FIXED)
        comment_btn = MDIconButton(icon="comment-outline")
        comment_lbl = MDLabel(text=str(state["replies"]), size_hint_x=None, width=dp(25))

        comment_btn.bind(
            on_release=lambda x, p=post, lbl=comment_lbl:
            self.open_comment_action_menu(x, p, lbl)
        )

        action_bar.add_widget(comment_btn)
        action_bar.add_widget(comment_lbl)

        # BOOKMARK
        bm_btn = MDIconButton(icon="bookmark-outline")
        bm_lbl = MDLabel(text=str(state["bookmarks"]), size_hint_x=None, width=dp(25))
        bm_btn.bind(on_release=lambda x, p=post: self.toggle_bookmark(post_id, bm_btn, bm_lbl, p))
        action_bar.add_widget(bm_btn)
        action_bar.add_widget(bm_lbl)

        # REPOST
        rp_btn = MDIconButton(icon="repeat")
        rp_lbl = MDLabel(text=str(state["reposts"]), size_hint_x=None, width=dp(25))
        rp_btn.bind(on_release=lambda x, p=post: self.toggle_repost(post_id, rp_btn, rp_lbl, p))
        action_bar.add_widget(rp_btn)
        action_bar.add_widget(rp_lbl)

        # SHARE
        share_btn = MDIconButton(icon="share-variant")
        share_btn.bind(on_release=lambda x, p=post: self.share_post(p))
        action_bar.add_widget(share_btn)

        card.add_widget(action_bar)

        return card

    # ================= COMMENT MENU (FIXED INDENTATION) =================
    def open_comment_action_menu(self, button, post, comment_lbl=None):
        items = [
            {
                "text": "💬 Comment",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.handle_comment(post)
            },
            {
                "text": "🔁 Quote Post",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.handle_comment(post)
            }
        ]

        self.menu = MDDropdownMenu(
            caller=button,
            items=items,
            width_mult=4
        )
        self.menu.open()

    def open_post_menu(self, button, post):
        items = [
            {"text": "🚫 Block User", "viewclass": "OneLineListItem", "on_release": lambda: self.block_user(post)},
            {"text": "🔇 Mute User", "viewclass": "OneLineListItem", "on_release": lambda: self.mute_user(post)},
            {"text": "🚨 Report Post", "viewclass": "OneLineListItem", "on_release": lambda: self.report_post(post)},
            {"text": "👤 View Profile", "viewclass": "OneLineListItem", "on_release": lambda: self.view_profile(post)},
            {"text": "🗑 Delete Post", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_post(post)}
        ]

        self.post_menu = MDDropdownMenu(caller=button, items=items, width_mult=5)
        self.post_menu.open()

    def block_user(self, post):
        try:
            requests.post(f"{self.USER_API}/block/{post.get('user_id')}", json={"current_user": self.user_id})
            print("🚫 User Blocked")
        except Exception as e: print(e)
        self.post_menu.dismiss()

    def mute_user(self, post):
        add_activity("muted_users", self.user_id, {"user_id": post.get("user_id"), "username": post.get("username")})
        print("🔇 User Muted")
        self.post_menu.dismiss()

    def report_post(self, post):
        add_activity("reports", self.user_id, post)
        print("🚨 Post Reported")
        self.post_menu.dismiss()

    def view_profile(self, post):
        try:
            profile = self.manager.get_screen("profile")
            profile.view_user_id = post.get("user_id")
            profile.view_username = post.get("username")
            if hasattr(profile, "load_profile"): profile.load_profile()
            self.manager.current = "profile"
        except Exception as e: print(e)
        self.post_menu.dismiss()

    def delete_post(self, post):
        try:
            post_id = post.get("id")
            requests.delete(f"{self.POST_API}/delete/{post_id}")
            self.load_posts()
            print("🗑 Post Deleted")
        except Exception as e: print(e)
        self.post_menu.dismiss()

    def handle_comment(self, post):
        add_activity("replies", self.user_id, {"post_id": post.get("id"), "username": post.get("username"), "text": post.get("text"), "image": post.get("image")})
        self.open_post_detail(post)

    def open_post_detail(self, post):
        screen = self.manager.get_screen("post_detail")
        screen.current_post_id = post.get("id")
        self.manager.current = "post_detail"

    def toggle_like(self, post_id, btn, lbl, post):

        s = self.post_state[post_id]

        if not s["liked"]:
            s["liked"] = True
            s["likes"] += 1

            add_activity("likes", self.user_id, {
                "post_id": post.get("id"),
                "username": post.get("username"),
                "text": post.get("text"),
                "image": post.get("image"),
                "source": post.get("source", "feed")
            })

            btn.icon = "heart"

        else:
            s["liked"] = False
            s["likes"] = max(0, s["likes"] - 1)

            remove_activity(
                "likes",
                self.user_id,
                post.get("id")
            )

            btn.icon = "heart-outline"

        lbl.text = str(s["likes"])


    def toggle_bookmark(self, post_id, btn, lbl, post):

        s = self.post_state[post_id]

        if not s["bookmarked"]:
            s["bookmarked"] = True
            s["bookmarks"] += 1

            add_activity("bookmarks", self.user_id, {
                "post_id": post.get("id"),
                "username": post.get("username"),
                "text": post.get("text"),
                "image": post.get("image"),
                "source": post.get("source", "feed")
            })

            btn.icon = "bookmark"

        else:
            s["bookmarked"] = False
            s["bookmarks"] = max(0, s["bookmarks"] - 1)

            remove_activity(
                "bookmarks",
                self.user_id,
                post.get("id")
            )

            btn.icon = "bookmark-outline"

        lbl.text = str(s["bookmarks"])


    def toggle_repost(self, post_id, btn, lbl, post):

        s = self.post_state[post_id]

        if not s["reposted"]:
            s["reposted"] = True
            s["reposts"] += 1

            add_activity("reposts", self.user_id, {
                "post_id": post.get("id"),
                "username": post.get("username"),
                "text": post.get("text"),
                "image": post.get("image"),
                "source": post.get("source", "feed")
            })

        else:
            s["reposted"] = False
            s["reposts"] = max(0, s["reposts"] - 1)

            remove_activity(
                "reposts",
                self.user_id,
                post.get("id")
            )

        lbl.text = str(s["reposts"])


    def share_post(self, post):

        add_activity("shares", self.user_id, {
            "post_id": post.get("id"),
            "username": post.get("username"),
            "text": post.get("text"),
            "image": post.get("image"),
            "source": post.get("source", "feed")
        })

        print("✅ Shared:", post.get("id"))

    # ================= NAV =================
    def goto_feed(self, x): self.manager.current = "feed"
    def goto_search(self, x): self.manager.current = "search"
    def goto_ai(self, x): self.manager.current = "ai"
    def goto_notifications(self, x): self.manager.current = "notifications"
    def goto_spaces(self, x): self.manager.current = "spaces"
    def goto_create_space(self, x): self.manager.current = "create_space"
    def goto_cyber_score(self, x): self.manager.current = "cyber_score"
    def goto_safe_browser(self, x): self.manager.current = "safe_browser"
    def goto_threat_alert(self, x): self.manager.current = "threat_alert"
    def goto_create_post(self, x): self.manager.current = "create_post"
    def goto_profile(self, x): self.manager.current = "profile"
    def goto_settings(self, x): self.manager.current = "settings"

    def on_size(self, *args): pass
