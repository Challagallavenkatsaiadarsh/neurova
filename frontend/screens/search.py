import os
import threading
import requests
from functools import partial

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem

from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import AsyncImage

from backend.core.activity_store import add_activity

API_URL = "http://127.0.0.1:5000/search/trending"

class SearchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user_id = "current_user"
        self.post_state = {}
        self.post_menu = None
        self.USER_API = "http://127.0.0.1:5000/api/user"
        self.POST_API = "http://127.0.0.1:5000/api/post"

        # ================= BACKGROUND =================
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        bg_path = os.path.join(base_dir, "assets", "images", "search.jpg")

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source=bg_path, pos=self.pos, size=self.size)
            Color(0, 0, 0, 0.55)
            self.overlay = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= ROOT LAYOUT =================
        root = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        
        # Header
        top_bar = MDBoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(10))
        top_bar.add_widget(MDIconButton(icon="arrow-left", on_release=self.go_back))
        top_bar.add_widget(MDLabel(text="Search", halign="left", bold=True))
        root.add_widget(top_bar)

        self.search_bar = MDTextField(hint_text="Search...", mode="round")
        search_box = MDBoxLayout(size_hint=(1, None), height=dp(50))
        search_box.add_widget(self.search_bar)
        root.add_widget(search_box)

        # ================= TRENDING TOPICS =================
        root.add_widget(MDLabel(text="Trending", size_hint_y=None, height=dp(30), bold=True))
        self.topic_scroll = MDScrollView(size_hint=(1, None), height=dp(50), do_scroll_x=True, do_scroll_y=False)
        self.topic_carousel = MDBoxLayout(orientation="horizontal", spacing=dp(10), adaptive_width=True)
        self.topic_scroll.add_widget(self.topic_carousel)
        root.add_widget(self.topic_scroll)

        # ================= TRENDING POSTS =================
        root.add_widget(MDLabel(text="Posts", size_hint_y=None, height=dp(30), bold=True))
        scroll = MDScrollView()
        self.results_area = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        self.results_area.bind(minimum_height=self.results_area.setter("height"))
        scroll.add_widget(self.results_area)
        root.add_widget(scroll)
        
        self.add_widget(root)

        self.load_trending_topics()
        self.load_trending_posts()

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.overlay.pos = self.pos
        self.overlay.size = self.size

    def go_back(self, *args):
        if self.manager: self.manager.current = "feed"

    def get_state(self, post_id):
        if post_id not in self.post_state:
            self.post_state[post_id] = {"liked": False, "bookmarked": False, "reposted": False, "likes": 0, "bookmarks": 0, "reposts": 0, "replies": 0}
        return self.post_state[post_id]

    def safe_add(self, activity_type, post):
        add_activity(activity_type, self.user_id, {"post_id": post.get("id"), "username": post.get("username"), "text": post.get("text")})

    # ================= ACTIONS =================
    def like_post(self, post, btn, lbl):
        s = self.get_state(post["id"])
        s["liked"] = not s["liked"]
        s["likes"] += 1 if s["liked"] else -1
        lbl.text = str(max(0, s["likes"]))
        btn.icon = "heart" if s["liked"] else "heart-outline"
        self.safe_add("likes", post)

    def comment_post(self, post, lbl):
        s = self.get_state(post["id"])
        s["replies"] += 1
        lbl.text = str(s["replies"])
        self.safe_add("replies", post)

    def repost_post(self, post, btn, lbl):
        s = self.get_state(post["id"])
        s["reposted"] = not s["reposted"]
        s["reposts"] += 1 if s["reposted"] else -1
        lbl.text = str(max(0, s["reposts"]))
        btn.icon = "repeat" if s["reposted"] else "repeat-outline"
        self.safe_add("reposts", post)

    def bookmark_post(self, post, btn, lbl):
        s = self.get_state(post["id"])
        s["bookmarked"] = not s["bookmarked"]
        s["bookmarks"] += 1 if s["bookmarked"] else -1
        lbl.text = str(max(0, s["bookmarks"]))
        btn.icon = "bookmark" if s["bookmarked"] else "bookmark-outline"
        self.safe_add("bookmarks", post)

    # ================= MENU =================
    def open_post_menu(self, button, post):
        if self.post_menu: self.post_menu.dismiss()
        items = [
            {"text": "🚫 Block User", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.block_user(post)},
            {"text": "🔇 Mute User", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.mute_user(post)},
            {"text": "🚨 Report Post", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.report_post(post)},
            {"text": "👤 View Profile", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.view_profile(post)},
            {"text": "🗑 Delete Post", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.delete_post(post)}
        ]
        self.post_menu = MDDropdownMenu(caller=button, items=items, width_mult=5)
        self.post_menu.open()

    def block_user(self, post): self.post_menu.dismiss(); print("Blocked")
    def mute_user(self, post): self.post_menu.dismiss(); print("Muted")
    def report_post(self, post): self.post_menu.dismiss(); print("Reported")
    def view_profile(self, post): self.post_menu.dismiss(); print("Viewing profile")
    def delete_post(self, post): self.post_menu.dismiss(); print("Deleted")

    # ================= CARD =================
    def create_card(self, post):
        s = self.get_state(post.get("id", "unknown"))
        card = MDCard(orientation="vertical", size_hint=(1, None), adaptive_height=True, padding=dp(10), spacing=dp(5), radius=[15], md_bg_color=(0.1, 0.1, 0.1, 1))

        header = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        header.add_widget(MDLabel(text=f"@{post.get('username','user')}", bold=True, size_hint_x=1))
        menu_btn = MDIconButton(icon="dots-vertical", size_hint=(None, None), size=(dp(40), dp(40)))
        menu_btn.bind(on_release=partial(self.open_post_menu, post=post))
        header.add_widget(menu_btn)
        card.add_widget(header)

        if post.get("text"):
            card.add_widget(MDLabel(text=post.get("text"), adaptive_height=True, padding=(dp(5), dp(5))))
        if post.get("image"):
            card.add_widget(AsyncImage(source=post["image"], size_hint_y=None, height=dp(200), allow_stretch=True))

        actions = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(0))
        
        # Like
        like_btn = MDIconButton(icon="heart-outline", size_hint=(None, None), size=(dp(40), dp(40)))
        like_lbl = MDLabel(text=str(s["likes"]), size_hint_x=None, width=dp(25), font_style="Caption")
        like_btn.bind(on_release=lambda x: self.like_post(post, like_btn, like_lbl))
        
        # Comment
        comment_btn = MDIconButton(icon="comment-outline", size_hint=(None, None), size=(dp(40), dp(40)))
        comment_lbl = MDLabel(text=str(s["replies"]), size_hint_x=None, width=dp(25), font_style="Caption")
        comment_btn.bind(on_release=lambda x: self.comment_post(post, comment_lbl))
        
        # Bookmark
        bm_btn = MDIconButton(icon="bookmark-outline", size_hint=(None, None), size=(dp(40), dp(40)))
        bm_lbl = MDLabel(text=str(s["bookmarks"]), size_hint_x=None, width=dp(25), font_style="Caption")
        bm_btn.bind(on_release=lambda x: self.bookmark_post(post, bm_btn, bm_lbl))
        
        # Repost
        repost_btn = MDIconButton(icon="repeat", size_hint=(None, None), size=(dp(40), dp(40)))
        repost_lbl = MDLabel(text=str(s["reposts"]), size_hint_x=None, width=dp(25), font_style="Caption")
        repost_btn.bind(on_release=lambda x: self.repost_post(post, repost_btn, repost_lbl))
        
        share_btn = MDIconButton(icon="share-variant", size_hint=(None, None), size=(dp(40), dp(40)))

        for w in [like_btn, like_lbl, comment_btn, comment_lbl, bm_btn, bm_lbl, repost_btn, repost_lbl, share_btn]:
            actions.add_widget(w)
            
        card.add_widget(actions)
        return card

    # ================= LOADERS =================
    def load_trending_topics(self):
        def worker():
            try:
                res = requests.get(API_URL, timeout=5)
                trending_data = res.json().get("trending", [])
            except: trending_data = []
            def update(dt):
                self.topic_carousel.clear_widgets()
                for t in trending_data[:10]:
                    tag = t.get('tag', '').replace('#', '')
                    btn = MDCard(size_hint=(None, None), size=(dp(100), dp(35)), radius=[15], md_bg_color=(0.2, 0.2, 0.2, 0.5))
                    btn.add_widget(MDLabel(text=f"#{tag}", halign="center", font_style="Caption"))
                    self.topic_carousel.add_widget(btn)
            Clock.schedule_once(update)
        threading.Thread(target=worker, daemon=True).start()

    def load_trending_posts(self):
        def worker():
            example_post = {"id": "test_01", "username": "Admin", "text": "This is an example trending post!"}
            try:
                res = requests.get(API_URL, timeout=5)
                posts_data = res.json().get("posts", [])
            except: posts_data = []
            if not posts_data: posts_data = [example_post]
            def update(dt):
                self.results_area.clear_widgets()
                for p in posts_data: self.results_area.add_widget(self.create_card(p))
            Clock.schedule_once(update)
        threading.Thread(target=worker, daemon=True).start()

    def trigger_search(self, *args):
        q = self.search_bar.text.strip()
        if q: self.on_search(None, q)

    def on_search(self, instance, text):
        def worker():
            try:
                res = requests.get(API_URL, timeout=5)
                posts_data = res.json().get("posts", [])
            except: posts_data = []
            def update(dt):
                self.results_area.clear_widgets()
                if not posts_data:
                    self.results_area.add_widget(MDLabel(text="No results found", halign="center"))
                    return
                for p in posts_data: self.results_area.add_widget(self.create_card(p))
            Clock.schedule_once(update)
        threading.Thread(target=worker, daemon=True).start()

    # ================= SEARCH =================
    def trigger_search(self, *args):
        q = self.search_bar.text.strip()
        if q: self.on_search(None, q)

    def on_search(self, instance, text):
        def worker():
            try:
                res = requests.get(API_URL, timeout=5)
                posts_data = res.json().get("posts", [])
            except: posts_data = []
            def update(dt):
                self.results_area.clear_widgets()
                if not posts_data:
                    self.results_area.add_widget(MDLabel(text="No results found", halign="center"))
                    return
                for p in posts_data: self.results_area.add_widget(self.create_card(p))
            Clock.schedule_once(update)
        threading.Thread(target=worker, daemon=True).start()
