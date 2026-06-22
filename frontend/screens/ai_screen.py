# =========================================
# FILE: frontend/screens/ai_screen.py (FINAL STABLE + FIT-TO-VIEW FIX)
# =========================================

import os
import threading
import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard

from kivy.graphics import Rectangle, Color
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from plyer import filechooser


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

AI_API_URL = "http://127.0.0.1:5000/ai/chat"


class AIScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_file = None

        # ================= BACKGROUND =================
        self.image_path = os.path.join(
            BASE_DIR, "frontend", "assets", "images", "neuroAI.jpg"
        )

        with self.canvas.before:
            self.bg = Rectangle(source=self.image_path, pos=self.pos, size=self.size)
            Color(0, 0, 0, 0.72)
            self.overlay = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= ROOT =================
        root = MDBoxLayout(orientation="vertical", padding=15, spacing=10)

        # ================= HEADER =================
        header = MDCard(
            orientation="horizontal", padding=15, spacing=10,
            size_hint=(1, None), height=80, radius=[22],
            md_bg_color=(0.03, 0.07, 0.06, 0.88)
        )

        ai_logo = AsyncImage(
            source=os.path.join(BASE_DIR, "frontend/assets/images/profile.jpg"),
            size_hint=(None, None), size=(50, 50)
        )

        ai_title = MDLabel(
            text="NeuroAI", theme_text_color="Custom",
            text_color=(0.25, 0.85, 0.65, 1), bold=True
        )

        header.add_widget(ai_logo)
        header.add_widget(ai_title)
        root.add_widget(header)

        # ================= CHAT AREA =================
        self.scroll = MDScrollView()
        self.chat_layout = MDBoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))
        self.scroll.add_widget(self.chat_layout)
        root.add_widget(self.scroll)

        # ================= INPUT =================
        input_box = MDBoxLayout(orientation="horizontal", padding=[10, 5, 10, 10])
        card = MDCard(
            orientation="horizontal", size_hint=(1, None), height=72,
            radius=[40], padding=[14, 5, 14, 5], spacing=8,
            md_bg_color=(0.06, 0.10, 0.11, 0.92)
        )

        attach = MDIconButton(icon="paperclip", on_release=self.open_file)
        mic = MDIconButton(icon="microphone", on_release=self.voice_input)
        self.input_box = TextInput(
            hint_text="Ask NeuroAI...", multiline=True,
            background_color=(0, 0, 0, 0), foreground_color=(1, 1, 1, 1)
        )
        send = MDIconButton(icon="arrow-up", on_release=self.send_message)

        card.add_widget(attach)
        card.add_widget(mic)
        card.add_widget(self.input_box)
        card.add_widget(send)
        input_box.add_widget(card)
        root.add_widget(input_box)
        self.add_widget(root)

    def safe_ui(self, func, *args):
        Clock.schedule_once(lambda dt: func(*args))

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.overlay.pos = self.pos
        self.overlay.size = self.size

    def open_file(self, instance):
        filechooser.open_file(on_selection=self.on_file)

    def on_file(self, selection):
        if selection:
            self.selected_file = selection[0]
            self.safe_ui(self.add_message, "System", f"📎 {self.selected_file}")

    def send_message(self, instance):
        message = self.input_box.text.strip()
        if not message: return
        self.safe_ui(self.add_message, "You", message)
        self.input_box.text = ""
        loading = self.add_message("NeuroAI", "⏳ Thinking...")
        threading.Thread(target=self.get_ai_response, args=(message, loading), daemon=True).start()

    def voice_input(self, instance):
        loading = self.add_message("NeuroAI", "🎤 Listening...")
        def worker():
            try:
                payload = {"username": "user", "message": "voice input"}
                r = requests.post(AI_API_URL, json=payload, timeout=180)
                try: data = r.json()
                except: data = {"success": False, "error": r.text}
                Clock.schedule_once(lambda dt: self.handle_response(data, loading))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_message("NeuroAI", f"Voice Error: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def get_ai_response(self, message, loading):
        try:
            payload = {"username": "user", "message": message}
            response = requests.post(AI_API_URL, json=payload, timeout=180)
            try: data = response.json()
            except: data = {"success": False, "error": response.text}
            Clock.schedule_once(lambda dt: self.handle_response(data, loading))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_message("NeuroAI", f"Backend Error: {e}"))

    def handle_response(self, data, loading):
        self._remove(loading)
        if not data.get("success"):
            self.safe_ui(self.add_message, "NeuroAI", data.get("error", "AI failed"))
            return

        rtype = data.get("type", "text")
        response = data.get("response", "")
        alerts = data.get("alerts", [])
        cyber_score = data.get("cyber_score", 0)
        image = data.get("image")

        if rtype == "image" and image:
            def build(dt):
                url = image.get("url")
                img_source = url if (url and url.startswith("http")) else None

                card = MDCard(
                    orientation="vertical", padding=10, spacing=10,
                    size_hint=(1, None), adaptive_height=True,
                    md_bg_color=(0.05, 0.12, 0.10, 0.90)
                )
                card.add_widget(MDLabel(text="🖼 Image Generated", bold=True))
                card.add_widget(MDLabel(text=image.get("prompt", "")))

                if img_source:
                    image_wrapper = MDBoxLayout(orientation="vertical", size_hint=(1, None), adaptive_height=True)
                    
                    img = AsyncImage(
                        source=img_source, size_hint=(1, None),
                        allow_stretch=True, keep_ratio=True
                    )

                    def resize_image(*args):
                        if not img.texture: return
                        tex_w, tex_h = img.texture.size
                        if tex_w <= 0 or tex_h <= 0: return

                        # Fit within 400x400 to ensure no swiping
                        max_w, max_h = 400, 400
                        scale = min(max_w / tex_w, max_h / tex_h)
                        
                        new_w = tex_w * scale
                        new_h = tex_h * scale
                        
                        img.height = new_h
                        image_wrapper.height = new_h
                        card._trigger_layout()

                    img.bind(texture=resize_image)
                    image_wrapper.add_widget(img)
                    card.add_widget(image_wrapper)
                else:
                    card.add_widget(MDLabel(text="❌ Image failed to load"))

                self.chat_layout.add_widget(card)
            Clock.schedule_once(build)
        else:
            self.safe_ui(self.add_message, "NeuroAI", response)

        if alerts:
            text = "⚠ Alerts:\n" + "\n".join(f"• {a}" for a in alerts)
            self.safe_ui(self.add_message, "NeuroAI", text)

        self.safe_ui(self.add_message, "NeuroAI", f"🛡 Cyber Score: {cyber_score}")

    def add_message(self, sender, message):
        card = MDCard(
            orientation="vertical", padding=15, spacing=8,
            size_hint=(1, None), adaptive_height=True,
            md_bg_color=(0.05, 0.12, 0.10, 0.90) if sender == "NeuroAI" else (0.08, 0.08, 0.08, 0.92)
        )
        
        # Add Sender Label
        card.add_widget(MDLabel(
            text=str(sender), bold=True, 
            size_hint_y=None, height=20,
            theme_text_color="Secondary"
        ))

        # Add Message Label with proper text wrapping/height binding
        msg_label = MDLabel(
            text=str(message),
            size_hint_y=None,
            valign="top"
        )
        
        def update_label_height(*args):
            msg_label.text_size = (msg_label.width, None)
            msg_label.height = msg_label.texture_size[1]
            card._trigger_layout()

        msg_label.bind(width=update_label_height)
        msg_label.bind(texture_size=update_label_height)
        
        card.add_widget(msg_label)
        self.chat_layout.add_widget(card)
        return card

    def _remove(self, widget):
        try: self.chat_layout.remove_widget(widget)
        except: pass
        
