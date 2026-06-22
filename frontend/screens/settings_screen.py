from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFlatButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from backend.settings_service import SettingsService
from backend.user_session import UserSession


class SettingsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog = None
        self.input_field = None
        self.bg = None
        self.listener = None

        # ================= FIREBASE =================
        self.service = SettingsService()
        self.user_id = str(UserSession.user_id).strip()

        self.service.ensure_user_settings(self.user_id)

        # ================= SETTINGS =================
        self.settings = self.service.get_settings(self.user_id) or {}

        # ================= REALTIME LISTENER =================
        self.listener = self.service.listen_settings(
            self.user_id,
            self.on_settings_update
        )

        # ================= BACKGROUND =================
        with self.canvas.before:
            Color(1, 1, 1, 1)

            self.bg = Rectangle(
                source=r"C:\Users\Admin\Documents\neurova\frontend\assets\images\settings.jpg",
                pos=self.pos,
                size=self.size
            )

        self.bind(size=self.update_bg, pos=self.update_bg)

        Clock.schedule_once(self.update_bg, 0)

        # ================= ROOT =================
        root = MDScrollView(do_scroll_x=False)

        self.container = MDBoxLayout(
            orientation="vertical",
            spacing=25,
            padding=[20, 40, 20, 40],
            size_hint_y=None,
            adaptive_height=True
        )

        # ================= TITLE =================
        title = MDBoxLayout(
            size_hint_y=None,
            height="70dp",
            spacing=10
        )

        title.add_widget(
            MDLabel(
                text="⚙",
                font_size="34sp",
                size_hint=(None, None),
                size=("40dp", "40dp"),
                theme_text_color="Custom",
                text_color=(0.25, 0.85, 0.65, 1)
            )
        )

        title.add_widget(
            MDLabel(
                text="Settings",
                font_size="22sp",
                theme_text_color="Custom",
                text_color=(0.25, 0.85, 0.65, 1)
            )
        )

        self.container.add_widget(title)

        # ================= SECTION =================
        def section(title_text):

            card = MDCard(
                orientation="vertical",
                padding=15,
                spacing=10,
                size_hint=(1, None),
                adaptive_height=True,
                md_bg_color=(0, 0, 0, 0.30),
                radius=[20]
            )

            label = MDLabel(
                text=title_text,
                size_hint_y=None,
                height=35,
                bold=True,
                theme_text_color="Custom",
                text_color=(0.3, 1, 0.8, 1)
            )

            inner = MDBoxLayout(
                orientation="vertical",
                spacing=10,
                size_hint_y=None,
                adaptive_height=True
            )

            card.add_widget(label)
            card.add_widget(inner)

            return card, inner

        # ================= BUTTON =================
        def action(text, callback):

            return MDFlatButton(
                text=text,
                size_hint_x=1,
                on_release=callback
            )

        # ================= SWITCH =================
        def switch_row(text, key, default=False):

            state = bool(self.settings.get(key, default))

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height="55dp",
                spacing=15
            )

            label = MDLabel(
                text=text,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 0.95)
            )

            switch = MDCard(
                size_hint=(None, None),
                size=("70dp", "34dp"),
                radius=[17],
                padding=2,
                md_bg_color=(
                    (0.25, 0.85, 0.65, 1)
                    if state else
                    (0.4, 0.4, 0.4, 1)
                )
            )

            thumb = MDCard(
                size_hint=(None, None),
                size=("28dp", "28dp"),
                radius=[14],
                md_bg_color=(1, 1, 1, 1)
            )

            switch_box = MDBoxLayout()

            def draw(current_state):

                switch.clear_widgets()
                switch_box.clear_widgets()

                switch.md_bg_color = (
                    (0.25, 0.85, 0.65, 1)
                    if current_state else
                    (0.4, 0.4, 0.4, 1)
                )

                if current_state:
                    switch_box.add_widget(MDLabel())
                    switch_box.add_widget(thumb)
                else:
                    switch_box.add_widget(thumb)
                    switch_box.add_widget(MDLabel())

                switch.add_widget(switch_box)

            draw(state)

            def toggle(*args):
                nonlocal state

                state = not state

                draw(state)

                self.service.update_setting(
                    self.user_id,
                    key,
                    state
                )

            switch.bind(on_release=toggle)

            row.add_widget(label)
            row.add_widget(switch)

            return row

        # ================= ACCOUNT =================
        account_card, account = section("👤 Account Settings")

        account.add_widget(
            action("Change Username", self.change_username)
        )

        account.add_widget(
            action("Change Password", self.change_password)
        )

        account.add_widget(
            action("Logout", self.logout)
        )

        self.container.add_widget(account_card)

        # ================= SECURITY =================
        security_card, security = section("🔐 Cybersecurity Settings")

        security.add_widget(
            switch_row("Phishing Detection", "phishing", True)
        )

        security.add_widget(
            switch_row("Link Scanner", "link_scanner", True)
        )

        security.add_widget(
            switch_row("Auto Block Links", "auto_block", True)
        )

        security.add_widget(
            switch_row("Threat Alerts", "threat_alerts", True)
        )

        self.container.add_widget(security_card)

        # ================= NOTIFICATIONS =================
        notif_card, notif = section("🔔 Notifications")

        notif.add_widget(
            switch_row("Push Notifications", "push", True)
        )

        notif.add_widget(
            switch_row("Email Notifications", "email", False)
        )

        notif.add_widget(
            switch_row("Threat Alerts", "notif_threat", True)
        )

        self.container.add_widget(notif_card)

        # ================= AI =================
        ai_card, ai = section("🤖 AI Settings")

        ai.add_widget(
            switch_row("AI Assistant", "ai", True)
        )

        ai.add_widget(
            switch_row("Fast Mode", "fast_mode", True)
        )

        ai.add_widget(
            switch_row("AI Memory", "memory", False)
        )

        self.container.add_widget(ai_card)

        # ================= UI =================
        ui_card, ui = section("🎨 UI Settings")

        ui.add_widget(
            switch_row("Dark Mode", "dark_mode", True)
        )

        ui.add_widget(
            switch_row("Reduce Animations", "animations", False)
        )

        self.container.add_widget(ui_card)

        # ================= BACK =================
        back = MDRoundFlatButton(
            text="BACK",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=("120dp", "45dp"),
            on_release=self.go_back
        )

        self.container.add_widget(back)

        root.add_widget(self.container)

        self.add_widget(root)

    # ================= REALTIME CALLBACK =================
    def on_settings_update(self, data):

        if data:
            self.settings = data

    # ================= BACKGROUND =================
    def update_bg(self, *args):

        if not self.bg:
            return

        w, h = self.size

        if not self.bg.texture:
            self.bg.pos = self.pos
            self.bg.size = self.size
            return

        img_w, img_h = self.bg.texture.size

        # KEEP ORIGINAL IMAGE RATIO
        scale = min(w / img_w, h / img_h)

        new_w = img_w * scale
        new_h = img_h * scale

        self.bg.size = (new_w, new_h)

        # CENTER IMAGE
        self.bg.pos = (
            self.x + (w - new_w) / 2,
            self.y + (h - new_h) / 2
        )

    # ================= USERNAME =================
    def change_username(self, instance):

        self.input_field = MDTextField(
            hint_text="Enter new username"
        )

        self.dialog = MDDialog(
            title="Change Username",
            type="custom",
            content_cls=self.input_field,
            buttons=[
                MDFlatButton(
                    text="SAVE",
                    on_release=self.save_username
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )

        self.dialog.open()

    def save_username(self, instance):

        username = self.input_field.text.strip()

        if username:
            self.service.change_username(
                self.user_id,
                username
            )

        self.dialog.dismiss()

    # ================= PASSWORD =================
    def change_password(self, instance):

        self.input_field = MDTextField(
            hint_text="Enter new password",
            password=True
        )

        self.dialog = MDDialog(
            title="Change Password",
            type="custom",
            content_cls=self.input_field,
            buttons=[
                MDFlatButton(
                    text="SAVE",
                    on_release=self.save_password
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )

        self.dialog.open()

    def save_password(self, instance):

        password = self.input_field.text.strip()

        if password:
            self.service.change_password(
                self.user_id,
                password
            )

        self.dialog.dismiss()

    # ================= LOGOUT =================
    def logout(self, instance):

        self.dialog = MDDialog(
            title="Logout",
            text="Are you sure you want to logout?",
            buttons=[
                MDFlatButton(
                    text="NO",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="YES",
                    on_release=self.confirm_logout
                )
            ]
        )

        self.dialog.open()

    def confirm_logout(self, instance):

        self.service.logout(self.user_id)

        UserSession.logout()

        self.dialog.dismiss()

        self.manager.current = "login"

    # ================= BACK =================
    def go_back(self, instance):

        self.manager.current = "feed"

    # ================= CLEANUP =================
    def on_leave(self):

        try:
            if self.listener:
                self.listener.unsubscribe()
        except:
            pass
