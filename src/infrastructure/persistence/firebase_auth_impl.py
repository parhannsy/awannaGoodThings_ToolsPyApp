"""
FirebaseAuthRepository
Menangani proses autentikasi login pengguna ke Firebase Auth REST API
dan mengambil profil pengguna dari Cloud Firestore.
"""

import requests
from src.infrastructure.config.firebase_config import FirebaseConfig

class FirebaseAuthRepository:
    def __init__(self):
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FirebaseConfig.API_KEY}"

    def login_user(self, email: str, password: str) -> dict:
        """
        Melakukan autentikasi email & password.
        Returns:
            dict: Data profil user jika sukses, None jika gagal.
        """
        auth_payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            # 1. Validasi Kredensial ke Firebase Authentication
            response = requests.post(self.auth_url, json=auth_payload, timeout=10)
            
            if response.status_code == 200:
                auth_data = response.json()
                local_id = auth_data["localId"] # Ini adalah idUser / UID
                
                # 2. Ambil Profil Detail dari Firestore menggunakan UID
                profile_data = self._get_user_profile(local_id)
                return profile_data
            else:
                print(f"[Auth Error] {response.text}")
                return None
                
        except Exception as e:
            print(f"[Network Error] Gagal melakukan login: {str(e)}")
            return None

    def _get_user_profile(self, uid: str) -> dict:
        """Mengambil dokumen user secara spesifik berdasarkan UID dokumen"""
        doc_url = f"{FirebaseConfig.get_firestore_url('users')}/{uid}"
        
        try:
            response = requests.get(doc_url, params={"key": FirebaseConfig.API_KEY}, timeout=10)
            if response.status_code == 200:
                doc_data = response.json()
                fields = doc_data.get("fields", {})
                
                # Parsing format REST API Firestore menjadi dictionary Python biasa
                profile = {
                    "idUser": fields.get("idUser", {}).get("stringValue", ""),
                    "email": fields.get("email", {}).get("stringValue", ""),
                    "nama": fields.get("nama", {}).get("stringValue", ""),
                    "panggilan": fields.get("panggilan", {}).get("stringValue", ""),
                    "role": fields.get("role", {}).get("stringValue", ""),
                    "isActive": fields.get("isActive", {}).get("booleanValue", False),
                }
                return profile
            return None
        except Exception as e:
            print(f"[Firestore Error] Gagal mengambil profil: {str(e)}")
            return None