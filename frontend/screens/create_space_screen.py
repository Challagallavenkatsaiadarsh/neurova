from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.graphics import Rectangle

import requests


class CreateSpaceScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ================= BACKGROUND =================
        with self.canvas.before:
            self.bg = Rectangle(
                source="assets/images/spaces_bg.jpg",
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= UI =================
        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        layout.add_widget(MDLabel(
            text="🎤 Create Space",
            halign="center",
            font_style="H4"
        ))

        self.space_name = MDTextField(
            hint_text="Space Name"
        )

        self.space_topic = MDTextField(
            hint_text="Topic (AI, Tech, etc.)"
        )

        self.create_btn = MDRaisedButton(
            text="Create & Enter Space",
            pos_hint={"center_x": 0.5},
            on_release=self.create_space
        )

        layout.add_widget(self.space_name)
        layout.add_widget(self.space_topic)
        layout.add_widget(self.create_btn)

        self.status = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        layout.add_widget(self.status)

        self.add_widget(layout)

    # ================= BACKGROUND =================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # ================= CREATE SPACE =================
    def create_space(self, instance):

        name = self.space_name.text.strip()
        topic = self.space_topic.text.strip()

        if not name or not topic:
            self.status.text = "❌ Name and topic required"
            return

        if len(name) < 3:
            self.status.text = "❌ Name too short"
            return

        self.create_btn.text = "Creating..."
        self.create_btn.disabled = True
        self.status.text = "⏳ Creating space..."

        try:
            # ================= 1. CREATE SPACE =================
            response = requests.post(
                "http://127.0.0.1:5000/spaces/create",
                json={
                    "name": name,
                    "topic": topic,
                    "host": "user"
                },
                timeout=5
            )

            data = response.json()

            if response.status_code != 200:
                self.status.text = f"❌ Backend Error"
                print(data)
                return

            space = data.get("space", {})
            space_id = space.get("space_id")

            if not space_id:
                self.status.text = "❌ Invalid space response"
                return

            print("✅ Space Created:", space_id)

            # ================= 2. JOIN SPACE =================
            requests.post(
                f"http://127.0.0.1:5000/spaces/join/{space_id}",
                json={"user": "user"},
                timeout=5
            )

            # ================= 3. GET LIVEKIT TOKEN (HOST) =================
            token_response = requests.post(
                "http://127.0.0.1:5002/token",
                json={
                    "user": "user",
                    "room": space_id,
                    "role": "host"
                },
                timeout=5
            )

            token_data = token_response.json()

            token = token_data.get("token")
            ws_url = token_data.get("url")

            if not token:
                self.status.text = "❌ Token generation failed"
                print(token_data)
                return

            print("🎤 LiveKit Token Ready")

            # ================= 4. STORE GLOBAL SESSION =================
            session = {
                "room_id": space_id,
                "name": name,
                "topic": topic,
                "user": "user",
                "role": "host",
                "token": token,
                "url": ws_url
            }

            # GLOBAL ACCESS (IMPORTANT FOR LIVE SCREEN)
            self.manager.selected_space = session

            print("🚀 Session stored:", session)

            # ================= 5. GO TO SPACES =================
            self.manager.current = "spaces"

        except requests.exceptions.ConnectionError:
            self.status.text = "❌ Backend not running"

        except requests.exceptions.Timeout:
            self.status.text = "❌ Timeout error"

        except Exception as e:
            self.status.text = f"❌ Error: {e}"
            print(e)

        finally:
            self.create_btn.text = "Create & Enter Space"
            self.create_btn.disabled = False
