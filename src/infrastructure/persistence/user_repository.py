"""
Infrastructure: UserRepository
Menangani sinkronisasi data profil pengguna ke Cloud Firestore via REST API.
"""

import threading
from typing import List, Dict, Any, Optional
import requests
from infrastructure.config.firebase_config import FirebaseConfig
from domain.repositories.user_repository import UserRepositoryPort


class UserRepository(UserRepositoryPort):
    def __init__(self, auth_repository=None):
        """
        Inisialisasi repository user menggunakan Firebase REST API.
        """
        self.auth_repo = auth_repository
        # Base URL untuk koleksi 'users' di Firestore REST API
        self.base_url = FirebaseConfig.get_firestore_url('users')

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Mengambil seluruh dokumen dari koleksi 'users' via Firestore REST API."""
        try:
            url = self.base_url
            response = requests.get(url, params={"key": FirebaseConfig.API_KEY}, timeout=10)
            
            if response.status_code != 200:
                print(f"[USER REPO ERROR] Gagal ambil semua user: {response.text}")
                return []
                
            data = response.json()
            documents = data.get("documents", [])
            
            result = []
            for doc in documents:
                # Mengambil nama dokumen terakhir sebagai UID/idUser jika field kosong
                doc_name = doc.get("name", "")
                fallback_uid = doc_name.split("/")[-1] if doc_name else ""
                
                fields = doc.get("fields", {})
                
                # Parsing format REST API Firestore ke Dict Python biasa
                user_profile = {
                    "idUser": fields.get("idUser", {}).get("stringValue", fallback_uid),
                    "email": fields.get("email", {}).get("stringValue", ""),
                    "nama": fields.get("nama", {}).get("stringValue", ""),
                    "panggilan": fields.get("panggilan", {}).get("stringValue", ""),
                    "role": fields.get("role", {}).get("stringValue", ""),
                    "isActive": fields.get("isActive", {}).get("booleanValue", True),
                    "isProfileComplete": fields.get("isProfileComplete", {}).get("booleanValue", False)
                }
                result.append(user_profile)
            return result
            
        except Exception as e:
            print(f"[USER REPO ERROR] Gagal mengambil data user: {e}")
            return []

    def get_all_teams(self) -> List[Dict[str, Any]]:
        """Mengambil seluruh dokumen dari koleksi 'teams' via Firestore REST API."""
        try:
            teams_url = FirebaseConfig.get_firestore_url('teams')
            response = requests.get(teams_url, params={"key": FirebaseConfig.API_KEY}, timeout=10)
            
            if response.status_code != 200:
                print(f"[USER REPO ERROR] Gagal ambil semua team: {response.text}")
                return []
                
            data = response.json()
            documents = data.get("documents", [])
            
            result = []
            for doc in documents:
                doc_name = doc.get("name", "")
                fallback_id = doc_name.split("/")[-1] if doc_name else ""
                fields = doc.get("fields", {})
                
                team_profile = {
                    "idTeam": fields.get("idTeam", {}).get("stringValue", fallback_id),
                    "nama": fields.get("nama", {}).get("stringValue", ""),
                    "panggilan": fields.get("panggilan", {}).get("stringValue", ""),
                    "alamat": fields.get("alamat", {}).get("stringValue", ""),
                    "nohp": fields.get("nohp", {}).get("stringValue", ""),
                    "role_tim": fields.get("role_tim", {}).get("stringValue", ""),
                    "isActive": fields.get("isActive", {}).get("booleanValue", True),
                    "tanggal_bergabung": fields.get("tanggal_bergabung", {}).get("timestampValue", "")
                }
                result.append(team_profile)
            return result
            
        except Exception as e:
            print(f"[USER REPO ERROR] Gagal mengambil data teams: {e}")
            return []

    def create_team_profile(self, team_data: dict) -> bool:
        """Membuat dokumen baru di koleksi 'teams' melalui Firestore REST API."""
        try:
            teams_url = FirebaseConfig.get_firestore_url('teams')
            firestore_fields = {}
            for key, value in team_data.items():
                if isinstance(value, bool):
                    firestore_fields[key] = {"booleanValue": value}
                elif isinstance(value, (int, float)):
                    firestore_fields[key] = {"integerValue" if isinstance(value, int) else "doubleValue": value}
                else:
                    firestore_fields[key] = {"stringValue": str(value)}

            payload = {"fields": firestore_fields}
            response = requests.post(f"{teams_url}?key={FirebaseConfig.API_KEY}", json=payload, timeout=10)

            if response.status_code in [200, 201]:
                print(f"[USER REPO] Berhasil membuat dokumen team baru")
                return True

            print(f"[USER REPO ERROR] Gagal membuat dokumen team: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            print(f"[USER REPO CRITICAL ERROR] Gagal membuat team profile: {e}")
            return False

    def update_user_profile(self, id_user: str, profile_data: dict) -> bool:
        """
        Memperbarui atau membuat dokumen profil user di Firestore via REST API Patch (UpdateMask).
        """
        try:
            if not id_user:
                print("[USER REPO ERROR] idUser kosong.")
                return False
                
            # URL spesifik ke dokumen user terkait
            doc_url = f"{self.base_url}/{id_user}"
            
            # Format payload dictionary Python biasa ke dalam struktur JSON Firestore REST API
            firestore_fields = {}
            update_masks = []
            
            for key, value in profile_data.items():
                update_masks.append(f"updateMask.fieldPaths={key}")
                if isinstance(value, bool):
                    firestore_fields[key] = {"booleanValue": value}
                elif isinstance(value, (int, float)):
                    firestore_fields[key] = {"integerValue" if isinstance(value, int) else "doubleValue": value}
                else:
                    firestore_fields[key] = {"stringValue": str(value)}
            
            payload = {"fields": firestore_fields}
            
            # Gabungkan parameter API Key dan Update Mask agar tidak menimpa field lama (bersifat Patch/Merge)
            mask_query = "&".join(update_masks)
            final_url = f"{doc_url}?key={FirebaseConfig.API_KEY}&{mask_query}"
            
            print(f"[USER REPO] Patching data ke Firestore REST API: {final_url}")
            response = requests.patch(final_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"[USER REPO] Berhasil sinkronisasi profil idUser: {id_user}")
                return True

            # Jika dokumen belum ada, coba buat dokumen baru menggunakan documentId yang sama
            if response.status_code == 404:
                print(f"[USER REPO] Dokumen tidak ditemukan, mencoba membuat baru: {id_user}")
                create_url = f"{self.base_url}?key={FirebaseConfig.API_KEY}&documentId={id_user}"
                create_response = requests.post(create_url, json=payload, timeout=10)
                if create_response.status_code == 200:
                    print(f"[USER REPO] Berhasil membuat profil baru idUser: {id_user}")
                    return True
                print(f"[USER REPO ERROR] Gagal membuat dokumen baru: {create_response.text}")
                return False

            print(f"[USER REPO ERROR] Gagal patch dokumen: {response.status_code} - {response.text}")
            return False
                
        except Exception as e:
            print(f"[USER REPO CRITICAL ERROR] Gagal sinkronisasi ke Firebase REST: {e}")
            return False

    def update_team_profile(self, team_id: str, profile_data: dict) -> bool:
        """Perbarui dokumen tim di koleksi 'teams' menggunakan Patch dengan updateMask."""
        try:
            if not team_id:
                print("[USER REPO ERROR] team_id kosong.")
                return False

            teams_url = FirebaseConfig.get_firestore_url('teams')
            doc_url = f"{teams_url}/{team_id}"

            firestore_fields = {}
            update_masks = []
            for key, value in profile_data.items():
                update_masks.append(f"updateMask.fieldPaths={key}")
                if isinstance(value, bool):
                    firestore_fields[key] = {"booleanValue": value}
                elif isinstance(value, (int, float)):
                    firestore_fields[key] = {"integerValue" if isinstance(value, int) else "doubleValue": value}
                else:
                    firestore_fields[key] = {"stringValue": str(value)}

            payload = {"fields": firestore_fields}
            mask_query = "&".join(update_masks)
            final_url = f"{doc_url}?key={FirebaseConfig.API_KEY}&{mask_query}"

            print(f"[USER REPO] Patching team data ke Firestore REST API: {final_url}")
            response = requests.patch(final_url, json=payload, timeout=10)

            if response.status_code == 200:
                print(f"[USER REPO] Berhasil sinkronisasi team id: {team_id}")
                return True

            if response.status_code == 404:
                print(f"[USER REPO] Dokumen team tidak ditemukan, mencoba membuat baru: {team_id}")
                create_url = f"{FirebaseConfig.get_firestore_url('teams')}?key={FirebaseConfig.API_KEY}&documentId={team_id}"
                create_response = requests.post(create_url, json=payload, timeout=10)
                if create_response.status_code in [200, 201]:
                    print(f"[USER REPO] Berhasil membuat team baru id: {team_id}")
                    return True
                print(f"[USER REPO ERROR] Gagal membuat dokumen team baru: {create_response.text}")
                return False

            print(f"[USER REPO ERROR] Gagal patch team dokumen: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            print(f"[USER REPO CRITICAL ERROR] Gagal sinkronisasi team ke Firebase REST: {e}")
            return False

    def stream_users_data(self, callback_function) -> Optional[Any]:
        """
        [REST API LIMITATION]
        Firestore REST API standar tidak mendukung koneksi persistent WebSocket `.stream()` bawaan SDK.
        Sebagai gantinya, kita gunakan teknik polling aman berinterval demi kestabilan UI.
        """
        import time
        class RESTStreamSimulator:
            def __init__(self, cb):
                self.cb = cb
                self.running = True
                self.thread = threading.Thread(target=self._loop, daemon=True)
                self.thread.start()
                
            def _loop(self):
                while self.running:
                    time.sleep(10)  # Cek perubahan data setiap 10 detik sekali
                    if self.running:
                        self.cb()
                        
            def close(self):
                self.running = False

        print("[USER REPO] Mengaktifkan REST Simulator Listener untuk sinkronisasi halaman.")
        return RESTStreamSimulator(callback_function)

    def stream_teams_data(self, callback_function) -> Optional[Any]:
        """
        Polling simulasi untuk koleksi teams yang tidak mendukung Firestore native stream.
        """
        import time
        class RESTStreamSimulator:
            def __init__(self, cb):
                self.cb = cb
                self.running = True
                self.thread = threading.Thread(target=self._loop, daemon=True)
                self.thread.start()
                
            def _loop(self):
                while self.running:
                    time.sleep(10)
                    if self.running:
                        self.cb()
                        
            def close(self):
                self.running = False

        print("[USER REPO] Mengaktifkan REST Simulator Listener untuk koleksi teams.")
        return RESTStreamSimulator(callback_function)
