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
    current_user = "user"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comment_state = {} 
        self.thread_state = {} 
        self.root_layout = MDBoxLayout(orientation="vertical")
        self.scroll = MDScrollView(do_scroll_x=False)
        self.content = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=dp(10))
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_layout.add_widget(self.scroll)
        self.add_widget(self.root_layout)
        self.editing_comment_id = None
        self.comment_input = None
        self.send_btn = None
        self.menu = None

    def on_pre_enter(self):
        if self.current_post_id: self.load_post(self.current_post_id)

    def load_post(self, post_id):
        try:
            res = requests.get(f"{self.BASE_URL}/feed", timeout=10)
            posts = res.json().get("posts", [])
            self.current_post = next((p for p in posts if str(p.get("id")) == str(post_id)), None)
            if self.current_post: self.render_post()
        except Exception as e: print("LOAD ERROR:", e)

    def render_post(self):
        self.content.clear_widgets()
        post = self.current_post
        self.content.add_widget(MDIconButton(icon="arrow-left", on_release=lambda x: self.go_back()))
        
        card = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(15), 
                      spacing=dp(10), radius=[20], md_bg_color=(0.1, 0.1, 0.1, 1))
        card.add_widget(MDLabel(text=f"@{post.get('username','user')}", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(25)))
        if post.get("image"): card.add_widget(AsyncImage(source=post["image"], size_hint_y=None, height=dp(250)))
        card.add_widget(MDLabel(text=post.get("text", ""), size_hint_y=None, height=dp(60)))
        self.content.add_widget(card)
        
        input_box = MDBoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        self.comment_input = MDTextField(hint_text="Write comment...")
        self.send_btn = MDRoundFlatButton(text="Post", on_release=lambda x: self.send_comment(self.current_post_id))
        input_box.add_widget(self.comment_input); input_box.add_widget(self.send_btn)
        self.content.add_widget(input_box)
        
        self.reply_list = MDBoxLayout(orientation="vertical", size_hint_y=None)
        self.reply_list.bind(minimum_height=self.reply_list.setter("height"))
        self.content.add_widget(self.reply_list)
        self.render_comments(post.get("comments", []), depth=0)
        self.scroll.scroll_y = 1

    def render_comments(self, comments, depth):
        for c in comments:
            self.add_comment_widget(c, depth)
            replies = c.get("replies", [])
            if replies:
                if self.thread_state.get(c.get("id"), False):
                    self.render_comments(replies, depth + 1)
                else:
                    btn = MDRoundFlatButton(text=f"View {len(replies)} replies", on_release=lambda x, c=c.get("id"): self.toggle_thread(c), pos_hint={"x": 0.1})
                    self.reply_list.add_widget(btn)

    def add_comment_widget(self, data, depth):
        cid = data.get("id")
        if cid not in self.comment_state:
            self.comment_state[cid] = {"liked": False, "bookmarked": False, "reposted": False, "likes": 0, "bookmarks": 0, "reposts": 0}
        
        state = self.comment_state[cid]
        block = MDBoxLayout(orientation="vertical", size_hint_y=None, padding=[depth * dp(20), 0, 0, 0])
        block.bind(minimum_height=block.setter("height"))
        
        card = MDCard(orientation="vertical", adaptive_height=True, radius=[18], padding=dp(10), spacing=dp(10), md_bg_color=(0.15, 0.15, 0.15, 1))
        card.add_widget(MDLabel(text=f"@{data.get('username', 'user')}", theme_text_color="Custom", text_color=(0.6, 0.8, 1, 1), size_hint_y=None, height=dp(20)))
        card.add_widget(MDLabel(text=data.get("text", ""), adaptive_height=True))
        
        if data.get("image"):
            card.add_widget(AsyncImage(source=data["image"], size_hint_y=None, height=dp(200), allow_stretch=True))
        
        actions = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(2))
        
        def create_action(icon, count, callback):
            box = MDBoxLayout(size_hint_x=None, width=dp(65), spacing=dp(2))
            btn = MDIconButton(icon=icon, on_release=callback)
            lbl = MDLabel(text=str(count), font_style="Caption", valign="middle")
            box.add_widget(btn); box.add_widget(lbl)
            return box

        actions.add_widget(MDIconButton(icon="comment-outline", on_release=lambda x: self.show_reply_input(cid)))
        actions.add_widget(create_action("heart" if state["liked"] else "heart-outline", state["likes"], lambda x: self.toggle_state(cid, "liked")))
        actions.add_widget(create_action("bookmark" if state["bookmarked"] else "bookmark-outline", state["bookmarks"], lambda x: self.toggle_state(cid, "bookmarked")))
        actions.add_widget(create_action("repeat-variant" if state["reposted"] else "repeat", state["reposts"], lambda x: self.toggle_state(cid, "reposted")))
        actions.add_widget(MDIconButton(icon="dots-vertical", on_release=lambda b: self.open_comment_menu(b, cid, data.get("text", ""))))
        
        card.add_widget(actions)
        block.add_widget(card)
        
        input_container = MDBoxLayout(orientation="vertical", size_hint_y=None, height=0)
        input_container.id = f"reply_container_{cid}"
        block.add_widget(input_container)
        self.reply_list.add_widget(block)

    def toggle_state(self, cid, key):
        counter_map = {"liked": "likes", "bookmarked": "bookmarks", "reposted": "reposts"}
        c_key = counter_map[key]
        self.comment_state[cid][key] = not self.comment_state[cid][key]
        self.comment_state[cid][c_key] += 1 if self.comment_state[cid][key] else -1
        self.load_post(self.current_post_id)

    def show_reply_input(self, cid):
        target = next((w for w in self.reply_list.walk() if hasattr(w, 'id') and w.id == f"reply_container_{cid}"), None)
        if target:
            if target.height == 0:
                target.height = dp(70)
                tf = MDTextField(hint_text="Reply..."); btn = MDRoundFlatButton(text="Send", on_release=lambda x: self.post_reply(cid, tf.text))
                target.add_widget(tf); target.add_widget(btn)
            else: target.clear_widgets(); target.height = 0

    def post_reply(self, cid, text):
        if text.strip():
            requests.post(f"{self.BASE_URL}/feed/comment/reply/{self.current_post_id}/{cid}", json={"text": text, "username": self.current_user})
            self.load_post(self.current_post_id)

    def toggle_thread(self, cid):
        self.thread_state[cid] = not self.thread_state.get(cid, False)
        self.load_post(self.current_post_id)

    def open_comment_menu(self, button, cid, text):
        if self.menu: self.menu.dismiss()
        self.menu = MDDropdownMenu(caller=button, items=[{"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.edit_comment(cid, text)}, {"text": "Delete", "viewclass": "OneLineListItem", "on_release": lambda x=None: self.delete_comment(cid)}], width_mult=3)
        self.menu.open()

    def edit_comment(self, cid, text):
        self.editing_comment_id = cid; self.comment_input.text = text; self.send_btn.text = "Update"; self.menu.dismiss()

    def delete_comment(self, cid):
        self.menu.dismiss(); requests.delete(f"{self.BASE_URL}/feed/comment/delete/{self.current_post_id}/{cid}"); self.load_post(self.current_post_id)

    def send_comment(self, post_id):
        text = self.comment_input.text.strip()
        if not text: return
        if self.editing_comment_id: requests.put(f"{self.BASE_URL}/feed/comment/edit/{self.current_post_id}/{self.editing_comment_id}", json={"text": text}); self.editing_comment_id = None
        else: requests.post(f"{self.BASE_URL}/feed/comment/{post_id}", json={"text": text, "username": self.current_user})
        self.comment_input.text = ""; self.send_btn.text = "Post"; self.load_post(self.current_post_id)

    def go_back(self): self.manager.current = "feed"
