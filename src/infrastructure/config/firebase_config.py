import os
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

class FirebaseConfig:
    API_KEY = os.getenv("FIREBASE_API_KEY") or "AIzaSyAOXtdlNhQ6EKySu2CZmMgNvYiVZhUjL28"
    PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    
    @classmethod
    def get_firestore_url(cls, collection_name: str) -> str:
        """Membuat URL REST API untuk Firestore"""
        return f"https://firestore.googleapis.com/v1/projects/{cls.PROJECT_ID}/databases/(default)/documents/{collection_name}"