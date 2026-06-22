from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.app import MDApp
import requests
from plyer import filechooser
import os
from io import BytesIO


class CreatePostScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_image = None
        self.md_bg_color = (0.03, 0.04, 0.08, 1)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        title = MDLabel(
            text="Create Post",
            halign="center",
            font_style="H4"
        )

        card = MDCard(
            orientation="vertical",
            padding=20,
            spacing=20,
            radius=[20]
        )

        self.post_input = MDTextField(
            hint_text="Share your thoughts...",
            multiline=True,
            mode="rectangle"
        )

        # =========================
        # LOCAL IMAGE PREVIEW (FIXED)
        # =========================
        self.image_preview = Image(
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=True
        )

        pick_image_btn = MDIconButton(
            icon="plus",
            icon_size="48sp",
            theme_text_color="Custom",
            text_color=(0.25, 0.85, 0.65, 1),
            on_release=self.open_file_chooser,
            pos_hint={"center_x": 0.5}
        )

        post_btn = MDRaisedButton(
            text="POST",
            on_release=self.post_created,
            pos_hint={"center_x": 0.5}
        )

        card.add_widget(self.post_input)
        card.add_widget(pick_image_btn)
        card.add_widget(self.image_preview)
        card.add_widget(post_btn)

        layout.add_widget(title)
        layout.add_widget(card)

        self.add_widget(layout)

    # =========================
    # FILE PICKER
    # =========================
    def open_file_chooser(self, instance):
        filechooser.open_file(
            on_selection=self.on_file_selected,
            filters=[("Images", "*.png", "*.jpg", "*.jpeg")]
        )

    def on_file_selected(self, selection):
        if selection:
            self.selected_image = selection[0]

            # 🔥 FORCE LOCAL DISPLAY (NO CLOUDINARY URL HERE)
            self.image_preview.source = self.selected_image
            self.image_preview.reload()

    # =========================
    # POST REQUEST
    # =========================
    def post_created(self, instance):

        text = self.post_input.text.strip()

        app = MDApp.get_running_app()
        user = getattr(app, "current_user", None)
        username = user.get("username") if user else "user"

        print(f"Uploading post: {text} by {username}")
        print("IMAGE:", self.selected_image)

        try:
            url = "http://127.0.0.1:5000/api/post/create"

            files = {}

            # =========================
            # SAFE FILE UPLOAD
            # =========================
            if self.selected_image:
                with open(self.selected_image, "rb") as file_obj:
                    files["image"] = file_obj

                    response = requests.post(
                        url,
                        data={
                            "username": username,
                            "text": text
                        },
                        files=files,
                        timeout=20
                    )

            else:
                response = requests.post(
                    url,
                    data={
                        "username": username,
                        "text": text
                    },
                    timeout=20
                )

            print("SERVER RESPONSE:", response.text)

            # =========================
            # SUCCESS RESET
            # =========================
            if response.status_code == 200:
                self.post_input.text = ""
                self.selected_image = None
                self.image_preview.source = ""

                self.manager.current = "feed"

            else:
                print("SERVER ERROR:", response.text)

        except Exception as e:
            print("POST ERROR:", str(e))
