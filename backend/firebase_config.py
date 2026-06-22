import firebase_admin
from firebase_admin import credentials, firestore

# Prevent duplicate initialization (VERY IMPORTANT)
if not firebase_admin._apps:

    cred = credentials.Certificate(
        r"C:\Users\Admin\Documents\neurova\firebase-service-account.json"
    )

    firebase_admin.initialize_app(cred)

# ✅ THIS MUST EXIST (your error is because of this)
db = firestore.client()
