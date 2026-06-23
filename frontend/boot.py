import os

def safe_kivy_boot():
    # ================= CI / GITHUB ACTIONS SAFE MODE =================
    if os.environ.get("CI") == "true":
        os.environ["KIVY_NO_ARGS"] = "1"
        os.environ["KIVY_WINDOW"] = "dummy"
        os.environ["KIVY_GL_BACKEND"] = "mock"
        os.environ["SDL_VIDEODRIVER"] = "dummy"
