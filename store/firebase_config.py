import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load Firebase service account key
cred = credentials.Certificate("C:\\Users\\Qasim\\Documents\\Credentials.json")  # 🔹 Update with your JSON key
firebase_admin.initialize_app(cred)

# Firestore Database instance
db = firestore.client()