# =========================================
# FILE: frontend/screens/onboarding_screen.py
# =========================================

import requests

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRoundFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.scrollview import MDScrollView

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class OnboardingScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user_id = None
        self.full_name = "sai challagalla venkatesai adarsh"
        self.suggestions = []
        self.selected_handle = ""

        # =========================
        # MAIN LAYOUT
        # =========================
        main_layout = BoxLayout(
            orientation="vertical",
            padding=[30, 50, 30, 50],
            spacing=15
        )

        main_layout.add_widget(Widget(size_hint_y=None, height=50))

        title = MDLabel(
            text="Complete Your Profile",
            halign="center",
            font_style="H5",
            bold=True
        )

        self.info_label = MDLabel(
            text="Choose your identity on Neurova",
            halign="center"
        )

        # =========================
        # DOB FIELD + CALENDAR
        # =========================
        dob_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="50dp",
            spacing=10
        )

        self.dob_input = MDTextField(
            hint_text="Select Date of Birth",
            mode="rectangle",
            readonly=True
        )

        dob_btn = MDIconButton(
            icon="calendar",
            on_release=self.open_calendar
        )

        dob_layout.add_widget(self.dob_input)
        dob_layout.add_widget(dob_btn)

        # =========================
        # USER ID FIELD
        # =========================
        self.handle_input = MDTextField(
            hint_text="Select User ID (@handle)",
            mode="rectangle",
            readonly=True
        )

        # =========================
        # BUTTONS
        # =========================
        fetch_btn = MDRoundFlatButton(
            text="GET USER ID SUGGESTIONS",
            pos_hint={"center_x": 0.5},
            on_release=self.fetch_suggestions
        )

        submit_btn = MDRoundFlatButton(
            text="COMPLETE SETUP",
            pos_hint={"center_x": 0.5},
            on_release=self.complete_onboarding
        )

        # =========================
        # CARD
        # =========================
        card = MDCard(
            orientation="vertical",
            padding=25,
            spacing=15,
            size_hint=(0.85, None),
            height=420,
            pos_hint={"center_x": 0.5},
            md_bg_color=(0, 0, 0, 0.4)
        )

        card.add_widget(self.info_label)
        card.add_widget(dob_layout)
        card.add_widget(self.handle_input)
        card.add_widget(fetch_btn)
        card.add_widget(submit_btn)

        main_layout.add_widget(title)
        main_layout.add_widget(card)

        self.add_widget(main_layout)

    # =========================
    # FETCH USER ID SUGGESTIONS
    # =========================
    def fetch_suggestions(self, instance):

        try:
            url = "http://127.0.0.1:5000/api/auth/username-suggestions"

            response = requests.post(
                url,
                json={"username": self.full_name},
                timeout=10
            )

            data = response.json()

            if response.status_code == 200 and data.get("success"):
                self.suggestions = data.get("suggestions", [])
                self.show_suggestion_dialog()

            else:
                MDDialog(
                    title="Error",
                    text=data.get("message", "Failed to load suggestions")
                ).open()

        except Exception as e:
            MDDialog(
                title="Error",
                text=str(e)
            ).open()

    # =========================
    # FIXED DIALOG (NO COLLISION)
    # =========================
    def show_suggestion_dialog(self):

        scroll = MDScrollView(
            size_hint_y=None,
            height=250
        )

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            size_hint_y=None
        )

        layout.bind(minimum_height=layout.setter("height"))

        for s in self.suggestions:

            btn = MDRoundFlatButton(
                text=s,
                size_hint_x=1,
                on_release=lambda x, val=s: self.select_handle(val)
            )
            layout.add_widget(btn)

        scroll.add_widget(layout)

        self.dialog = MDDialog(
            title="Choose User ID (@handle)",
            type="custom",
            content_cls=scroll,
            auto_dismiss=True
        )

        self.dialog.open()

    def select_handle(self, handle):
        self.selected_handle = handle
        self.handle_input.text = handle

        if hasattr(self, "dialog"):
            self.dialog.dismiss()

    # =========================
    # CALENDAR FIXED
    # =========================
    def open_calendar(self, instance):

        try:
            picker = MDDatePicker()

            def on_save(inst, value, date_range):
                self.dob_input.text = str(value)

            picker.bind(on_save=on_save)
            picker.open()

        except Exception as e:
            MDDialog(
                title="Error",
                text=str(e)
            ).open()

    # =========================
    # COMPLETE ONBOARDING
    # =========================
    def complete_onboarding(self, instance):

        dob = self.dob_input.text.strip()
        handle = self.handle_input.text.strip()

        if not dob or not handle:
            MDDialog(
                title="Error",
                text="Please select DOB and User ID"
            ).open()
            return

        try:
            url = "http://127.0.0.1:5000/api/auth/complete-onboarding"

            response = requests.post(
                url,
                json={
                    "user_id": self.manager.user_id,
                    "date_of_birth": dob,
                    "user_id_handle": handle
                },
                timeout=10
            )

            data = response.json()

            if response.status_code == 200 and data.get("success"):

                MDDialog(
                    title="Success",
                    text="Onboarding completed!"
                ).open()

                self.manager.current = "feed"

            else:
                MDDialog(
                    title="Error",
                    text=data.get("message", "Failed to complete onboarding")
                ).open()

        except Exception as e:
            MDDialog(
                title="Error",
                text=str(e)
            ).open()
