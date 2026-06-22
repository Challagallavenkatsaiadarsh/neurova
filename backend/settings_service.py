import os
from google.cloud import firestore
from google.oauth2 import service_account

# ================= FIREBASE AUTH FIX =================
KEY_PATH = r"C:\Users\Admin\Documents\neurova\backend\config\serviceAccountKey.json"

if not os.path.exists(KEY_PATH):
    raise FileNotFoundError(f"Firebase key not found at {KEY_PATH}")

credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
db = firestore.Client(credentials=credentials)


class SettingsService:

    COLLECTION = "user_settings"

    def __init__(self):
        # store listener reference (IMPORTANT FIX)
        self._listener = None

    # ---------------- CREATE DEFAULT SETTINGS ----------------
    def ensure_user_settings(self, user_id):

        if not user_id:
            return

        ref = db.collection(self.COLLECTION).document(user_id)

        if not ref.get().exists:
            ref.set({
                "dark_mode": True,
                "phishing": True,
                "ai": True,
                "push": True,
                "email": False,
                "memory": False,
                "fast_mode": True,
                "link_scanner": True,
                "auto_block": True,
                "threat_alerts": True,
                "notif_threat": True,
                "animations": False
            })

    # ---------------- GET SETTINGS ----------------
    def get_settings(self, user_id):

        if not user_id:
            return {}

        ref = db.collection(self.COLLECTION).document(user_id)
        doc = ref.get()

        if doc.exists:
            data = doc.to_dict()

            # 🔥 FIX: ensure defaults always exist (prevents toggle freeze)
            defaults = {
                "dark_mode": True,
                "phishing": True,
                "ai": True,
                "push": True,
                "email": False,
                "memory": False,
                "fast_mode": True,
                "link_scanner": True,
                "auto_block": True,
                "threat_alerts": True,
                "notif_threat": True,
                "animations": False
            }

            for k, v in defaults.items():
                if k not in data:
                    data[k] = v

            return data

        return {}

    # ---------------- UPDATE SINGLE SETTING ----------------
    def update_setting(self, user_id, key, value):

        if not user_id:
            return

        ref = db.collection(self.COLLECTION).document(user_id)

        # ensure document exists
        if not ref.get().exists:
            self.ensure_user_settings(user_id)

        # 🔥 SAFE WRITE (prevents overwrite issues)
        ref.set({key: bool(value)}, merge=True)

    # ---------------- REAL-TIME LISTENER ----------------
    def listen_settings(self, user_id, callback):

        if not user_id:
            return None

        ref = db.collection(self.COLLECTION).document(user_id)

        # 🔥 FIX: stop old listener if exists
        if self._listener:
            try:
                self._listener.unsubscribe()
            except:
                pass

        def on_snapshot(doc_snapshot, changes, read_time):
            try:
                for doc in doc_snapshot:
                    if doc.exists:
                        callback(doc.to_dict())
                    else:
                        callback({})
            except Exception as e:
                print("Listener error:", e)

        self._listener = ref.on_snapshot(on_snapshot)
        return self._listener

    # ---------------- STOP LISTENER ----------------
    def stop_listener(self):
        if self._listener:
            try:
                self._listener.unsubscribe()
            except:
                pass
            self._listener = None

    # ---------------- USER ACTIONS ----------------
    def change_username(self, user_id, username):

        if not user_id:
            return

        db.collection("users").document(user_id).set({
            "username": username
        }, merge=True)

    def change_password(self, user_id, password):

        if not user_id:
            return

        db.collection("users").document(user_id).set({
            "password": password
        }, merge=True)

    # ---------------- LOGOUT ----------------
    def logout(self, user_id):
        pass
