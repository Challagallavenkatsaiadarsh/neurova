import os 
os.environ["KIVY_WINDOW"] = "dummy" 
os.environ["SDL_VIDEODRIVER"] = "dummy" 
os.environ["KIVY_GL_BACKEND"] = "mock" 
 
from kivy.config import Config 
Config.set("graphics", "visible", "0") 
Config.set("graphics", "window_state", "hidden") 
