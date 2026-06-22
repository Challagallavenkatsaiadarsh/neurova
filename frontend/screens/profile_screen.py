import os
import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDTextButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu

from kivy.uix.image import AsyncImage
from kivy.graphics import Rectangle, Color
from kivy.metrics import dp

from backend.core.activity_store import (
    add_activity,
    remove_activity,
    get_activity
)

class ProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user_id = "current_user"
        self.profile_user_id = "target_user_123" 
        self.API_URL = "http://127.0.0.1:5000/api/feed"
        self.USER_API = "http://127.0.0.1:5000/api/user"
        self.is_following = False
        self.notifications_enabled = False 
        self.post_state = {}

        # Background
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        bg_path = os.path.join(base_dir, "assets", "images", "profile.jpg")
        with self.canvas.before:
            self.bg = Rectangle(source=bg_path, pos=self.pos, size=self.size)
            Color(0, 0, 0, 0.45)
            self.overlay = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # UI Structure
        scroll = MDScrollView()
        self.root = MDBoxLayout(orientation="vertical", padding=20, spacing=12, size_hint_y=None)
        self.root.bind(minimum_height=self.root.setter("height"))

        self.profile_card = MDCard(
            orientation="vertical", padding=15, spacing=12, size_hint=(1, None),
            adaptive_height=True, radius=[25], md_bg_color=(0.05, 0.08, 0.12, 0.85)
        )

        # Header Elements
        cover_box = MDBoxLayout(size_hint_y=None, height=180)
        cover_box.add_widget(AsyncImage(source="https://picsum.photos/800/300"))
        pic_box = MDBoxLayout(size_hint_y=None, height=130)
        pic_box.add_widget(AsyncImage(source="https://picsum.photos/200"))

        self.username_label = MDLabel(text="User", halign="center")
        self.handle_label = MDLabel(text="@user", halign="center")
        self.bio_label = MDLabel(text="Bio here", halign="center")
        
        # Action Row
        action_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), adaptive_width=True, pos_hint={"center_x": 0.5})
        self.follow_btn = MDIconButton(icon="account-plus", on_release=self.toggle_follow)
        self.notification_btn = MDIconButton(icon="bell-plus", on_release=self.toggle_user_notifications)
        action_row.add_widget(self.follow_btn)
        action_row.add_widget(self.notification_btn)

        # Navigation
        row1 = MDBoxLayout(size_hint_y=None, height=50, spacing=40)
        self.followers_btn = MDTextButton(text="Followers: 0", on_release=lambda x: self.go_to_screen("followers_screen"))
        self.following_btn = MDTextButton(text="Following: 0", on_release=lambda x: self.go_to_screen("following_screen"))
        row1.add_widget(self.followers_btn)
        row1.add_widget(self.following_btn)

        row2 = MDBoxLayout(size_hint_y=None, height=45, spacing=15)
        for icon, cat in [("heart-outline", "likes"), ("comment-outline", "replies"), 
                          ("repeat", "reposts"), ("share-variant", "shares"), ("bookmark-outline", "bookmarks")]:
            btn = MDIconButton(icon=icon, size_hint=(None, None), size=(dp(40), dp(40)))
            btn.bind(on_release=lambda x, c=cat: self.refresh_and_load(c))
            row2.add_widget(btn)

        self.posts_container = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(18), padding=[0, dp(10), 0, dp(20)])
        self.posts_container.bind(minimum_height=self.posts_container.setter("height"))

        # Assemble
        for w in [cover_box, pic_box, self.username_label, self.handle_label, self.bio_label, action_row, row1, row2, self.posts_container]:
            self.profile_card.add_widget(w)

        self.root.add_widget(self.profile_card)
        scroll.add_widget(self.root)
        self.add_widget(scroll)

    # --- Feature Logic ---
    def toggle_user_notifications(self, *args):
        self.notifications_enabled = not self.notifications_enabled
        self.notification_btn.icon = "bell-minus" if self.notifications_enabled else "bell-plus"
        if self.notifications_enabled:
            add_activity("user_subscriptions", self.current_user_id, {"target": self.profile_user_id})
        else:
            remove_activity("user_subscriptions", self.current_user_id, self.profile_user_id)

    def toggle_follow(self, *args):
        self.is_following = not self.is_following
        self.follow_btn.icon = "account-check" if self.is_following else "account-plus"
        count = int(self.followers_btn.text.split(":")[1].strip())
        self.followers_btn.text = f"Followers: {count + 1 if self.is_following else max(0, count - 1)}"

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

    # --- Advanced Menu Actions ---
    def block_user(self, post):
        try:
            requests.post(f"{self.USER_API}/block/{post.get('user_id')}", json={"current_user": self.current_user_id})
        except Exception as e: print(e)
        self.post_menu.dismiss()

    def mute_user(self, post):
        add_activity("muted_users", self.current_user_id, {"user_id": post.get("user_id")})
        self.post_menu.dismiss()

    def view_profile(self, post):
        self.manager.current = "profile"
        self.post_menu.dismiss()

    def delete_post(self, post):
        try:
            requests.delete(f"{self.API_URL}/delete/{post.get('id')}")
            self.refresh_and_load("likes") 
        except Exception as e: print(e)
        self.post_menu.dismiss()

    def report_post(self, post):
        add_activity("reports", self.current_user_id, post)
        self.post_menu.dismiss()

    def share_post(self, post):
        add_activity("shares", self.current_user_id, {"post_id": post.get("id")})
        self.post_menu.dismiss()

    def create_post_card(self, post, category):
        post_id = post.get("id")
        card = MDCard(size_hint_y=None, adaptive_height=True, padding=[dp(12)]*4, radius=[15])
        layout = MDBoxLayout(orientation="vertical", spacing=dp(10), adaptive_height=True)
        
        header = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        header.add_widget(MDLabel(text=f"@{post.get('username', 'user')}"))
        menu_btn = MDIconButton(icon="dots-vertical")
        menu_btn.bind(on_release=lambda x, p=post: self.open_post_menu(x, p))
        header.add_widget(menu_btn)
        layout.add_widget(header)

        if post.get("text"): layout.add_widget(MDLabel(text=post["text"], adaptive_height=True))
        
        action_bar = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # All actions included
        actions = [("heart-outline", None), ("comment-outline", None), 
                   ("repeat", None), ("bookmark-outline", None), ("share-variant", lambda x: self.share_post(post))]
        
        for icon, callback in actions:
            btn = MDIconButton(icon=icon)
            if callback: btn.bind(on_release=callback)
            action_bar.add_widget(btn)
        
        layout.add_widget(action_bar)
        card.add_widget(layout)
        return card

    def load_posts(self, category):
        activities = get_activity(category, self.current_user_id) or []
        for act in activities:
            self.posts_container.add_widget(self.create_post_card(act, category))

    def refresh_and_load(self, category):
        self.posts_container.clear_widgets()
        self.load_posts(category)

    def go_to_screen(self, screen_name):
        if self.manager: self.manager.current = screen_name

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.overlay.pos = self.pos
        self.overlay.size = self.size
