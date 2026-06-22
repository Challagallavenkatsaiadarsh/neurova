from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle


class LiveSpaceScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # =========================
        # BACKGROUND IMAGE
        # =========================
        with self.canvas.before:
            self.bg = Rectangle(
                source="C:/Users/Admin/Documents/neurova/frontend/assets/images/spaces_bg.jpg",
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        title = MDLabel(
            text="LIVE SPACE",
            halign="center",
            font_style="H4",
            bold=True
        )

        room_title = MDLabel(
            text="IPL LIVE FAN DISCUSSION",
            halign="center",
            font_style="H5"
        )

        listeners = MDLabel(
            text="3.2K Listening Live",
            halign="center"
        )

        speakers = MDLabel(
            text="Host + 4 Co-Hosts Speaking",
            halign="center"
        )

        leave_btn = MDRoundFlatButton(
            text="LEAVE SPACE",
            pos_hint={"center_x": 0.5},
            on_release=self.leave_space
        )

        layout.add_widget(title)
        layout.add_widget(room_title)
        layout.add_widget(listeners)
        layout.add_widget(speakers)
        layout.add_widget(leave_btn)

        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def leave_space(self, instance):
        self.manager.current = "spaces"
