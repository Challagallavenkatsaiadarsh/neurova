from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.scrollview import MDScrollView

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.app import App  # ✅ Required to touch core application helper layers

import requests


class SpacesScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ✅ FIXED: Stripped the trailing slash to prevent Flask routing to an HTML 404 page
        self.API_URL = "http://127.0.0.1:5000/spaces"

        self.refresh_event = None

        # =====================================================
        # BACKGROUND
        # =====================================================
        with self.canvas.before:

            Color(1, 1, 1, 1)

            self.bg = Rectangle(
                source="assets/images/spaces_bg.jpg",
                pos=self.pos,
                size=self.size
            )

            # DARK OVERLAY
            Color(0, 0, 0, 0.55)

            self.overlay = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )

        # =====================================================
        # ROOT
        # =====================================================
        self.root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        # =====================================================
        # TITLE
        # =====================================================
        title = MDLabel(
            text="🎤 LIVE SPACES",
            halign="center",
            bold=True,
            font_style="H4",
            size_hint_y=None,
            height=60,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        self.root.add_widget(title)

        # =====================================================
        # SCROLL
        # =====================================================
        self.scroll = MDScrollView()

        self.spaces_layout = BoxLayout(
            orientation="vertical",
            spacing=18,
            padding=[0, 0, 0, 40],
            size_hint_y=None
        )

        self.spaces_layout.bind(
            minimum_height=self.spaces_layout.setter("height")
        )

        self.scroll.add_widget(self.spaces_layout)

        self.root.add_widget(self.scroll)

        self.add_widget(self.root)

        # =====================================================
        # INITIAL LOAD
        # =====================================================
        Clock.schedule_once(
            lambda dt: self.load_spaces(),
            1
        )

    # =====================================================
    # ON ENTER
    # =====================================================
    def on_enter(self, *args):

        try:

            if self.refresh_event:
                self.refresh_event.cancel()

            self.refresh_event = Clock.schedule_interval(
                self.auto_refresh,
                5
            )

            print("✅ Auto refresh restarted")

        except Exception as e:

            print("Refresh restart error:", e)

    # =====================================================
    # ON LEAVE
    # =====================================================
    def on_leave(self, *args):

        try:

            if self.refresh_event:

                self.refresh_event.cancel()

                self.refresh_event = None

                print("🛑 Auto refresh stopped")

        except Exception as e:

            print("Refresh stop error:", e)

    # =====================================================
    # BACKGROUND UPDATE
    # =====================================================
    def update_bg(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.overlay.pos = self.pos
        self.overlay.size = self.size

    # =====================================================
    # AUTO REFRESH
    # =====================================================
    def auto_refresh(self, dt):

        self.load_spaces()

    # =====================================================
    # LOAD SPACES
    # =====================================================
    def load_spaces(self):

        print("🎤 Loading spaces...")

        self.spaces_layout.clear_widgets()

        response = None
        try:

            response = requests.get(
                self.API_URL,
                timeout=5
            )

            data = response.json()

            print("✅ API RESPONSE:", data)

            spaces = data.get("spaces", [])

        except Exception as e:

            print("❌ Backend Error:", e)
            
            # ✅ Diagnostic Fallback: Let's view exactly what text Flask spit back if it isn't JSON
            if response is not None:
                print("RAW BACKEND RESPONSE:", response.text)

            self.spaces_layout.add_widget(
                MDLabel(
                    text=f"Backend Error:\n{e}",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 0.3, 0.3, 1)
                )
            )

            return

        # =====================================================
        # NO SPACES
        # =====================================================
        if not spaces:

            self.spaces_layout.add_widget(
                MDLabel(
                    text="🚫 No Live Spaces Running",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            )

            return

        # =====================================================
        # SPACE CARDS
        # =====================================================
        for space in spaces:

            print("🎧 SPACE FOUND:", space)

            room_id = space.get("id")

            name = space.get(
                "name",
                "Untitled Space"
            )

            topic = space.get(
                "topic",
                "General"
            )

            host = space.get(
                "host",
                "Unknown"
            )

            listeners = space.get(
                "listeners",
                0
            )

            # =====================================================
            # CARD
            # =====================================================
            card = MDCard(
                orientation="vertical",
                size_hint=(1, None),
                adaptive_height=True,
                padding=20,
                spacing=12,
                radius=[28],
                ripple_behavior=True,
                md_bg_color=(0.02, 0.06, 0.08, 0.92)
            )

            # LIVE LABEL
            card.add_widget(
                MDLabel(
                    text="🔴 LIVE NOW",
                    bold=True,
                    size_hint_y=None,
                    height=30,
                    theme_text_color="Custom",
                    text_color=(1, 0.25, 0.25, 1)
                )
            )

            # SPACE NAME
            card.add_widget(
                MDLabel(
                    text=f"🎧 {name}",
                    bold=True,
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=(0.2, 1, 0.85, 1)
                )
            )

            # TOPIC
            card.add_widget(
                MDLabel(
                    text=f"🧠 Topic: {topic}",
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            )

            # HOST
            card.add_widget(
                MDLabel(
                    text=f"👑 Host: @{host}",
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=(0.9, 0.9, 0.9, 1)
                )
            )

            # LISTENERS
            card.add_widget(
                MDLabel(
                    text=f"👥 {listeners} Listening",
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=(0.7, 1, 0.7, 1)
                )
            )

            # =====================================================
            # JOIN BUTTON
            # =====================================================
            join_btn = MDRoundFlatButton(
                text="JOIN SPACE",
                pos_hint={"center_x": 0.5}
            )

            join_btn.bind(
                on_release=lambda btn, s=space:
                self.join_space(s)
            )

            card.add_widget(join_btn)

            self.spaces_layout.add_widget(card)

    # =====================================================
    # JOIN SPACE (UPDATED HANDSHAKE HOOK)
    # =====================================================
    def join_space(self, space):
        """Triggers clean native token requests and opens the audio room."""
        try:
            room_id = space.get("id")
            print(f"🎤 Action Triggered: Joining Space ID {room_id}")

            # Cancel background polling interval loops to prevent UI desyncs during swap
            if self.refresh_event:
                self.refresh_event.cancel()

            # ✅ Dispatch connection hook cleanly to App orchestrator using explicit key identifiers
            app = App.get_running_app()
            app.join_live_space(space_id=room_id, username="NeuroAdmin")

        except Exception as e:
            print("❌ Client Interface Exception on Space Join:", e)
