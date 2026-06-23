import os

def safe_kivy_boot():
    os.environ["KIVY_WINDOW"] = "sdl2"
    os.environ["KIVY_GL_BACKEND"] = "sdl2"
