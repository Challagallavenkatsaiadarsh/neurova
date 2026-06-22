import sys
import os
import requests

# =====================================================
# ADD PROJECT ROOT TO PYTHON PATH
# =====================================================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# =====================================================
# KIVYMD
# =====================================================
from kivymd.app import MDApp

# =====================================================
# SCREEN MANAGER
# =====================================================
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import FadeTransition

# =====================================================
# AUTH SCREENS
# =====================================================
from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
from screens.onboarding_screen import OnboardingScreen

# =====================================================
# MAIN APP SCREENS
# =====================================================
from screens.feed_screen import FeedScreen
from screens.create_post_screen import CreatePostScreen
from screens.profile_screen import ProfileScreen
from screens.search import SearchScreen
from screens.post_detail_screen import PostDetailScreen

# =====================================================
# SETTINGS
# =====================================================
from screens.settings_screen import SettingsScreen

# =====================================================
# AI SYSTEM
# =====================================================
from screens.ai_screen import AIScreen

# =====================================================
# SECURITY SYSTEM
# =====================================================
from screens.security_center import SecurityCenterScreen
from screens.threat_alert_screen import ThreatAlertScreen
from screens.safe_browser_screen import SafeBrowserScreen
from screens.cyber_score_screen import CyberScoreScreen

# =====================================================
# NOTIFICATIONS
# =====================================================
from screens.notifications_screen import NotificationsScreen

# =====================================================
# SPACES SYSTEM
# =====================================================
from screens.spaces_screen import SpacesScreen
from screens.create_space_screen import CreateSpaceScreen
from screens.live_discussion_screen import LiveDiscussionScreen

# =====================================================
# 🔥 ADD FOLLOWERS SYSTEM (MISSING FIX)
# =====================================================
from screens.followers_screen import FollowersScreen
from screens.following_screen import FollowingScreen


# =====================================================
# MAIN APP
# =====================================================
class NeurovaApp(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"

        self.sm = MDScreenManager(
            transition=FadeTransition(duration=0.25)
        )

        # =====================================================
        # AUTH SCREENS
        # =====================================================
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignupScreen(name="signup"))
        self.sm.add_widget(OnboardingScreen(name="onboarding"))

        # =====================================================
        # MAIN APP SCREENS
        # =====================================================
        self.sm.add_widget(FeedScreen(name="feed"))
        self.sm.add_widget(CreatePostScreen(name="create_post"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(SearchScreen(name="search"))
        self.sm.add_widget(PostDetailScreen(name="post_detail"))

        # =====================================================
        # SETTINGS
        # =====================================================
        self.sm.add_widget(SettingsScreen(name="settings"))

        # =====================================================
        # AI SYSTEM
        # =====================================================
        self.sm.add_widget(AIScreen(name="ai"))

        # =====================================================
        # SECURITY SYSTEM
        # =====================================================
        self.sm.add_widget(SecurityCenterScreen(name="security_center"))
        self.sm.add_widget(ThreatAlertScreen(name="threat_alert"))
        self.sm.add_widget(SafeBrowserScreen(name="safe_browser"))
        self.sm.add_widget(CyberScoreScreen(name="cyber_score"))

        # =====================================================
        # NOTIFICATIONS
        # =====================================================
        self.sm.add_widget(NotificationsScreen(name="notifications"))

        # =====================================================
        # SPACES SYSTEM
        # =====================================================
        self.sm.add_widget(SpacesScreen(name="spaces"))
        self.sm.add_widget(CreateSpaceScreen(name="create_space"))
        self.sm.add_widget(LiveDiscussionScreen(name="live_discussion"))

        # =====================================================
        # 🔥 FOLLOWERS SYSTEM (FIX ADDED)
        # =====================================================
        self.sm.add_widget(FollowersScreen(name="followers_screen"))
        self.sm.add_widget(FollowingScreen(name="following_screen"))

        # =====================================================
        # START SCREEN
        # =====================================================
        self.sm.current = "login"

        return self.sm

    # =====================================================
    # ✅ CENTRAL LIVEKIT HANDSHAKE DISPATCHER
    # =====================================================
    def join_live_space(self, space_id, username="NeuroAdmin"):
        """Fetches tokens from Flask and delivers them seamlessly to LiveKit."""
        try:
            print(f"[API] Contacting backend to join room: {space_id} as {username}...")
            backend_url = f"http://127.0.0.1:5000/api/spaces/join/{space_id}"
            
            # Request valid JWT payload from our PyJWT backend logic
            response = requests.post(backend_url, json={"username": username}, timeout=5.0)
            
            if response.status_code == 200:
                space_data = response.json()
                print("[API] Cryptographic handshake token successfully obtained!")
                
                # Fetch target screen object from widget tree
                live_screen = self.sm.get_screen("live_discussion")
                
                # Directly bind token properties to trigger the background watchdog
                live_screen.set_space_data(space_data)
                
                # Switch views
                self.sm.current = "live_discussion"
            else:
                print(f"[API ERROR] Server refused entry context: {response.text}")
                
        except Exception as e:
            print(f"[CRITICAL FE] Cannot bridge connection to backend API on Port 5002: {e}")


if __name__ == "__main__":
    NeurovaApp().run()
