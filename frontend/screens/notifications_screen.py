import os

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard

from kivy.metrics import dp
from kivy.graphics import Rectangle, Color


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


class NotificationsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.active_tab = "all"
        self.user_id = "current_user"

        # ================= BACKGROUND =================
        with self.canvas.before:
            self.bg = Rectangle(
                source=os.path.join(BASE_DIR, "assets", "images", "bg4.jpg"),
                pos=self.pos,
                size=self.size
            )
            Color(0, 0, 0, 0.60)
            self.overlay = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= ROOT =================
        root = MDBoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )

        # ================= TOP BAR =================
        top_bar = MDBoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(10)
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back
        )

        title = MDLabel(
            text="Notifications",
            halign="left",
            bold=True
        )

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)

        root.add_widget(top_bar)

        # ================= TABS =================
        self.tab_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(12)
        )

        self.all_btn = MDRaisedButton(
            text="ALL",
            on_release=lambda x: self.switch_tab("all")
        )

        self.verified_btn = MDRaisedButton(
            text="VERIFIED",
            on_release=lambda x: self.switch_tab("verified")
        )

        self.tab_layout.add_widget(self.all_btn)
        self.tab_layout.add_widget(self.verified_btn)

        root.add_widget(self.tab_layout)

        # ================= SCROLL =================
        self.scroll = MDScrollView()

        self.list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        self.add_widget(root)

        self.update_tabs_ui()
        self.load_notifications()

    # =========================================================
    # BACK BUTTON → FEED
    # =========================================================
    def go_back(self, *args):
        if self.manager:
            self.manager.current = "feed"

    # =========================================================
    # REAL NOTIFICATIONS ONLY (NO TEST DATA)
    # =========================================================
    def get_notifications(self):
        """
        Hook this to backend / Firebase / Appwrite later
        """
        return []

    # =========================================================
    # CLICK → FEED SCREEN
    # =========================================================
    def open_feed_with_post(self, post_id):
        feed = self.manager.get_screen("feed")
        feed.selected_post_id = post_id
        self.manager.current = "feed"

    # =========================================================
    # LOAD NOTIFICATIONS (TEXT ONLY)
    # =========================================================
    def load_notifications(self):

        self.list_layout.clear_widgets()

        all_notifs = self.get_notifications()

        if self.active_tab == "verified":
            all_notifs = [n for n in all_notifs if n.get("verified", False)]

        if not all_notifs:
            self.list_layout.add_widget(
                MDLabel(
                    text="🔕 No notifications yet",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 0.7)
                )
            )
            return

        for item in all_notifs:

            post_id = item.get("post_id")

            card = MDCard(
                padding=dp(10),
                size_hint=(1, None),
                height=dp(70),
                radius=[12],
                md_bg_color=(0.02, 0.04, 0.03, 0.85)
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(3)
            )

            # ================= ONLY TEXT =================
            layout.add_widget(
                MDLabel(
                    text=f"@{item.get('user')}: {item.get('text')}",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 0.9),
                    size_hint_y=None,
                    height=dp(40)
                )
            )

            card.add_widget(layout)

            # CLICK → FEED (ALL ACTIONS HAPPEN THERE)
            if post_id:
                card.bind(
                    on_release=lambda x, pid=post_id: self.open_feed_with_post(pid)
                )

            self.list_layout.add_widget(card)

    # =========================================================
    # TAB UI
    # =========================================================
    def update_tabs_ui(self):
        active = (0.2, 0.85, 0.65, 1)
        inactive = (0.12, 0.12, 0.12, 1)

        self.all_btn.md_bg_color = active if self.active_tab == "all" else inactive
        self.verified_btn.md_bg_color = active if self.active_tab == "verified" else inactive

    def switch_tab(self, tab):
        self.active_tab = tab
        self.update_tabs_ui()
        self.load_notifications()

    # =========================================================
    # BACKGROUND
    # =========================================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.overlay.pos = self.pos
        self.overlay.size = self.size
