import os

# ================= SAFE CI FIX =================
# Prevent Kivy crashing in headless environments (GitHub Actions / Windows runner)
if os.environ.get("CI") == "true":
    os.environ["KIVY_WINDOW"] = "sdl2"
    os.environ["KIVY_GL_BACKEND"] = "sdl2"
    os.environ["SDL_VIDEODRIVER"] = "windows"

# ================= IMPORT APP =================
from frontend.main import MainApp

# ================= RUN APP =================
if __name__ == "__main__":
    MainApp().run()
