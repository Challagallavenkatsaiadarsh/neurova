import threading
import requests
import webbrowser
from urllib.parse import urlparse

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog

from kivy.clock import Clock
from kivy.graphics import Rectangle


API_URL = "http://127.0.0.1:5000/safe_browser/scan"


class SafeBrowserScreen(MDScreen):

    SAFE_DOMAINS = {
        "google.com",
        "youtube.com",
        "github.com",
        "openai.com",
        "microsoft.com",
        "apple.com",
        "wikipedia.org",
        "facebook.com",
        "instagram.com",
        "amazon.com"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.last_url = None
        self.last_hash = None
        self.requesting = False

        with self.canvas.before:
            self.bg_rect = Rectangle(
                source="C:/Users/Admin/Documents/neurova/frontend/assets/images/safe_browser.png",
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=12,
            spacing=12
        )

        header = MDCard(
            padding=12,
            radius=[25],
            size_hint=(1, None),
            height=120,
            md_bg_color=(0.02, 0.02, 0.05, 0.9)
        )

        header.add_widget(MDLabel(
            text="🌌 Cyber Singularity Browser (LEVEL 20)",
            halign="center",
            bold=True
        ))

        self.root_layout.add_widget(header)

        url_bar = MDBoxLayout(size_hint=(1, None), height=60, spacing=8)

        self.url_input = MDTextField(
            hint_text="Enter URL for Quantum Scan",
            mode="round"
        )

        go_btn = MDIconButton(
            icon="shield-search",
            on_release=self.scan_url
        )

        url_bar.add_widget(self.url_input)
        url_bar.add_widget(go_btn)

        self.root_layout.add_widget(url_bar)

        self.scroll = MDScrollView()

        self.result_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=12,
            size_hint_y=None
        )

        self.result_layout.bind(
            minimum_height=self.result_layout.setter("height")
        )

        self.scroll.add_widget(self.result_layout)
        self.root_layout.add_widget(self.scroll)

        self.add_widget(self.root_layout)

    # =========================
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    # =========================
    def normalize_domain(self, url):
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "").lower()
        except:
            return url

    # =========================
    def is_safe_domain(self, url):
        return self.normalize_domain(url) in self.SAFE_DOMAINS

    # =========================
    def open_browser(self, url):
        try:
            webbrowser.open(url)
        except:
            pass

    # =========================
    def safe_post(self, url):
        try:
            res = requests.post(API_URL, json={"url": url}, timeout=12)
            return res.json()
        except Exception as e:
            return {
                "safe": False,
                "status": "ERROR",
                "score": 0,
                "confidence": 0,
                "intent": "UNKNOWN",
                "threats": [str(e)]
            }

    # =========================
    def scan_url(self, instance):

        if self.requesting:
            return

        url = self.url_input.text.strip()

        if not url:
            MDDialog(title="Empty URL", text="Enter a valid URL").open()
            return

        if not url.startswith("http"):
            url = "https://" + url

        # 🔥 CLEAR OLD RESULTS (FIX ADDED)
        self.result_layout.clear_widgets()

        # SAFE DOMAIN SHORT-CIRCUIT
        if self.is_safe_domain(url):
            self.add_result(
                "🟢 TRUSTED DOMAIN (WHITELIST)",
                f"{url}\nThis domain is verified safe.",
                True
            )
            self.open_browser(url)
            return

        if url == self.last_url:
            return

        self.last_url = url
        self.requesting = True

        def worker():
            data = self.safe_post(url)

            def ui(dt):
                self.update_ui(url, data)
                self.auto_block_logic(data)
                self.requesting = False  # FIX: reset here safely

            Clock.schedule_once(ui)

        threading.Thread(target=worker, daemon=True).start()

    # =========================
    def auto_block_logic(self, data):

        safe = data.get("safe", True)
        intent = data.get("intent", "")
        score = data.get("score", 0)
        confidence = data.get("confidence", 0)

        if (
            not safe
            or intent in ["MALICIOUS", "CRITICAL_THREAT"]
            or score < 55
            or confidence < 60
        ):
            self.open_browser(
                "https://www.google.com/search?q=cyber+security+warning"
            )

    # =========================
    def format_threats(self, threats):
        return "\n".join(str(t) for t in threats)

    # =========================
    def update_ui(self, url, data):

        safe = data.get("safe", True)
        status = data.get("status", "")
        score = data.get("score", 0)
        confidence = data.get("confidence", 0)
        intent = data.get("intent", "")
        drift = data.get("drift", 0)
        reasons = data.get("reasons", [])

        key = f"{url}-{status}-{score}-{confidence}-{intent}"
        if key == self.last_hash:
            return
        self.last_hash = key

        if safe:
            self.add_result(
                "🟢 QUANTUM SAFE SITE",
                f"{url}\nSTATUS: {status}\nSCORE: {score}\nCONF: {confidence}\nINTENT: {intent}",
                True
            )
            self.open_browser(url)

        elif status == "RISK":
            self.add_result(
                "🟡 QUANTUM RISK DETECTED",
                f"{url}\nSTATUS: {status}\nSCORE: {score}\nCONF: {confidence}\nDRIFT: {drift}",
                False
            )

        else:
            self.add_result(
                "🔴 QUANTUM THREAT BLOCKED",
                f"{url}\nSTATUS: {status}\nSCORE: {score}\nCONF: {confidence}\nINTENT: {intent}\n\n"
                + self.format_threats(reasons),
                False
            )

            MDDialog(
                title="🚨 CYBER SINGULARITY ALERT",
                text="High probability malicious site detected!"
            ).open()

    # =========================
    def add_result(self, title, message, safe=True):

        card = MDCard(
            padding=15,
            radius=[20],
            adaptive_height=True,
            md_bg_color=(0.05, 0.15, 0.1, 0.85) if safe else (0.2, 0.05, 0.05, 0.9)
        )

        card.add_widget(MDLabel(text=title, bold=True))
        card.add_widget(MDLabel(text=message))

        self.result_layout.add_widget(card)
