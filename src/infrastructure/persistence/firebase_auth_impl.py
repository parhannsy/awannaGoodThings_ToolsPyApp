"""
FirebaseAuthRepository
Menangani proses autentikasi login pengguna ke Firebase Auth REST API
dan mengambil profil pengguna dari Cloud Firestore.
"""

import requests
from typing import Optional, Dict
from infrastructure.config.firebase_config import FirebaseConfig
from domain.repositories.auth_repository import AuthRepository


class FirebaseAuthRepository(AuthRepository):
    def __init__(self):
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FirebaseConfig.API_KEY}"

    def login_user(self, email: str, password: str) -> dict:
        """
        Melakukan autentikasi email & password.
        Returns:
            dict: Data profil user jika sukses.
        Raises:
            ValueError: Jika kredensial invalid atau Firebase menolak login.
        """
        auth_payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(self.auth_url, json=auth_payload, timeout=10)
            if response.status_code == 200:
                auth_data = response.json()
                local_id = auth_data.get("localId")
                if not local_id:
                    raise ValueError("Firebase gagal mengembalikan UID untuk sesi login.")

                profile_data = self._get_user_profile(local_id)
                if not profile_data:
                    return self._build_minimal_profile(local_id, email)
                return profile_data

            error_message = self._parse_firebase_error(response)
            print(f"[Auth Error] {error_message}")
            raise ValueError(error_message)

        except requests.RequestException as e:
            print(f"[Network Error] Gagal melakukan login: {str(e)}")
            raise ValueError("Gagal terhubung ke server autentikasi. Periksa koneksi internet Anda.")
        except Exception as e:
            raise

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
                    "idUser": fields.get("idUser", {}).get("stringValue", uid),
                    "email": fields.get("email", {}).get("stringValue", ""),
                    "nama": fields.get("nama", {}).get("stringValue", ""),
                    "panggilan": fields.get("panggilan", {}).get("stringValue", ""),
                    "alamat": fields.get("alamat", {}).get("stringValue", ""),
                    "nohp": fields.get("nohp", {}).get("stringValue", ""),
                    "bank": fields.get("bank", {}).get("stringValue", ""),
                    "nomor_rekening": fields.get("nomor_rekening", {}).get("stringValue", ""),
                    "role": fields.get("role", {}).get("stringValue", "advertiser"),
                    "isActive": fields.get("isActive", {}).get("booleanValue", True),
                    "isProfileComplete": fields.get("isProfileComplete", {}).get("booleanValue", False),
                }
                return profile
            print(f"[Firestore Error] User profile fetch failed: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"[Firestore Error] Gagal mengambil profil: {str(e)}")
            return None

    def _build_minimal_profile(self, uid: str, email: str = "") -> dict:
        return {
            "idUser": uid,
            "email": email,
            "nama": "",
            "panggilan": "",
            "alamat": "",
            "nohp": "",
            "bank": "",
            "nomor_rekening": "",
            "role": "advertiser",
            "isActive": True,
            "isProfileComplete": False,
        }

    def _parse_firebase_error(self, response):
        try:
            data = response.json()
            error_data = data.get("error", {})
            message = error_data.get("message")
        except ValueError:
            message = response.text

        if not message:
            return f"HTTP {response.status_code}"

        normalized_message = str(message).upper().strip()
        message_mappings = {
            "INVALID_PASSWORD": "Password salah.",
            "EMAIL_NOT_FOUND": "Email tidak ditemukan.",
            "USER_DISABLED": "Akun Anda dinonaktifkan.",
            "INVALID_EMAIL": "Format email tidak valid.",
            "INVALID_LOGIN_CREDENTIALS": "Kredensial login tidak valid.",
            "EMAIL_EXISTS": "Email sudah terdaftar.",
            "WEAK_PASSWORD": "Password minimal harus 6 karakter.",
            "OPERATION_NOT_ALLOWED": "Operasi tidak diizinkan pada konfigurasi Firebase Auth.",
        }

        for key, friendly in message_mappings.items():
            if key in normalized_message:
                return friendly

        return str(message).replace("_", " ").capitalize()

    def sign_up(self, email: str, password: str) -> Optional[str]:
        sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FirebaseConfig.API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        try:
            response = requests.post(sign_up_url, json=payload, timeout=10)
            if response.status_code == 200:
                local_id = response.json().get("localId")
                if not local_id:
                    raise ValueError("Firebase tidak mengembalikan UID setelah pendaftaran.")
                return local_id

            error_message = self._parse_firebase_error(response)
            print(f"[Auth SignUp Error] {error_message}")
            raise ValueError(error_message)
        except Exception as e:
            error_message = str(e)
            print(f"[Auth SignUp Error] Gagal mendaftar: {error_message}")
            raise ValueError(error_message)
