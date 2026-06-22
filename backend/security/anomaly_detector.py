# =========================================
# FILE: backend/security/anomaly_detector.py
# =========================================

import os
import json

from datetime import datetime


class AnomalyDetector:

    def __init__(self):

        # =========================================
        # BASE DIRECTORY
        # =========================================
        base_dir = os.path.dirname(__file__)

        # =========================================
        # LOGS FOLDER
        # =========================================
        self.logs_dir = os.path.join(
            base_dir,
            "logs"
        )

        # CREATE LOGS DIRECTORY
        os.makedirs(self.logs_dir, exist_ok=True)

        # =========================================
        # LOGIN HISTORY FILE
        # =========================================
        self.login_db = os.path.join(
            self.logs_dir,
            "login_history.json"
        )

        # CREATE FILE IF NOT EXISTS
        if not os.path.exists(self.login_db):

            with open(self.login_db, "w") as file:
                json.dump({}, file)

    # =========================================
    # LOAD LOGIN HISTORY
    # =========================================
    def load_history(self):

        try:

            with open(self.login_db, "r") as file:
                return json.load(file)

        except:
            return {}

    # =========================================
    # SAVE LOGIN HISTORY
    # =========================================
    def save_history(self, history):

        with open(self.login_db, "w") as file:
            json.dump(history, file, indent=4)

    # =========================================
    # MAIN DETECTION
    # =========================================
    def detect(self, previous_data, current_data):

        alerts = []

        if previous_data.get("country") != current_data.get("country"):
            alerts.append("🌍 Login from new country detected")

        if previous_data.get("device") != current_data.get("device"):
            alerts.append("💻 New device detected")

        current_hour = datetime.now().hour

        if current_hour < 5:
            alerts.append("🌙 Unusual login time detected")

        return alerts

    # =========================================
    # LOGIN ANOMALY SYSTEM
    # =========================================
    def check_login(self, email, device_id):

        history = self.load_history()

        current_data = {
            "device": device_id,
            "country": "India",
            "time": str(datetime.now())
        }

        # =========================================
        # FIRST LOGIN
        # =========================================
        if email not in history:

            history[email] = current_data

            self.save_history(history)

            return False

        # =========================================
        # DETECT ANOMALIES
        # =========================================
        previous_data = history[email]

        alerts = self.detect(
            previous_data,
            current_data
        )

        # UPDATE HISTORY
        history[email] = current_data

        self.save_history(history)

        return len(alerts) > 0


# =========================================
# SIMPLE FUNCTION VERSION
# =========================================
def detect_login_anomaly(email, device_id):

    detector = AnomalyDetector()

    return detector.check_login(
        email,
        device_id
    )
