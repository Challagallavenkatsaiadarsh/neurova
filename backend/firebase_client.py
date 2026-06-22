import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "config", "serviceAccountKey.json")

# =========================
# SAFE INITIALIZATION
# =========================
if not firebase_admin._apps:

    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"Firebase service account key not found at: {cred_path}"
        )

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# =========================
# FIRESTORE CLIENT
# =========================
db = firestore.client()
