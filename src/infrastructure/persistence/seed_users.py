"""
Seeder Users (Fire Auth + Firestore)
Skrip utilitas profesional untuk mendaftarkan akun awal langsung ke Firebase Authentication
dan menyinkronkan profil datanya ke Cloud Firestore menggunakan REST API resmi.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Menambahkan root directory proyek ke sys.path agar module src bisa terbaca
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.infrastructure.config.firebase_config import FirebaseConfig

# Memuat konfigurasi variabel lingkungan (.env)
load_dotenv()

def seed_complete_user_account():
    print("=== MEMULAI PROSES SEEDING (FIRE AUTH + FIRESTORE) ===")
    
    api_key = FirebaseConfig.API_KEY
    project_id = FirebaseConfig.PROJECT_ID
    
    if not api_key or not project_id:
        print("[ERROR] Gagal membaca file .env. Pastikan API KEY dan PROJECT ID sudah terisi.")
        return

    # Data Akun yang kamu minta
    email_user = "akunmentor@gmail.com"
    password_user = "Bismillah123/" # Fire Auth otomatis meng-hash password ini di server Google

    # ==========================================
    # LAKUKAN REGISTRASI KE FIREBASE AUTHENTICATION
    # ==========================================
    print("[1/2] Mendaftarkan kredensial akun ke Firebase Auth...")
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    
    auth_payload = {
        "email": email_user,
        "password": password_user,
        "returnSecureToken": True
    }

    try:
        auth_response = requests.post(auth_url, json=auth_payload, timeout=10)
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            # UID unik yang digenerate otomatis oleh Firebase Authentication
            firebase_uid = auth_data["localId"]
            print(f"[SUKSES AUTH] User terdaftar di Fire Auth. UID: {firebase_uid}")
        elif auth_response.status_code == 400 and "EMAIL_EXISTS" in auth_response.text:
            print("[WARN AUTH] Email sudah terdaftar di Fire Auth. Melewati langkah registrasi auth...")
            # Jika sudah ada, kita butuh UID-nya. Silakan hapus user di konsol jika ingin reset ulang.
            print("[INFO] Harap bersihkan user di Firebase Console jika ingin memperbarui UID via seeder.")
            return
        else:
            print(f"[GAGAL AUTH] Gagal mendaftarkan user ke Fire Auth: {auth_response.text}")
            return

    except Exception as e:
        print(f"[NET ERROR] Gagal menghubungi Firebase Auth: {str(e)}")
        return

    # ==========================================
    # SINKRONISASI DATA PROFIL KE CLOUD FIRESTORE
    # ==========================================
    print("\n[2/2] Menyinkronkan data profil lengkap ke Cloud Firestore...")
    firestore_url = FirebaseConfig.get_firestore_url("users")
    
    # Payload profil lengkap sesuai spesifikasi data Firestore REST API
    firestore_payload = {
        "fields": {
            "idUser": {"stringValue": firebase_uid}, # DISINKRONKAN: Menggunakan UID dari Fire Auth
            "email": {"stringValue": email_user},
            "nama": {"stringValue": "agung gunawan"},
            "panggilan": {"stringValue": "mentor aja"},
            "alamat": {"stringValue": "Bojong, cilimus"},
            "nohp": {"stringValue": "080000000000"},
            "role": {"stringValue": "mentor"},
            "isActive": {"booleanValue": True},
            "bank": {"stringValue": "BCA"},
            "nomor_rekening": {"stringValue": "0000000000"}
        }
    }

    try:
        # Gunakan firebase_uid sebagai ID Dokumen agar relasi data berindeks rapih (1-to-1)
        params = {
            "key": api_key,
            "documentId": firebase_uid
        }
        
        firestore_response = requests.post(firestore_url, json=firestore_payload, params=params, timeout=10)
        
        if firestore_response.status_code == 200:
            print("\n=============================================")
            print("🎉 SEEDING BERHASIL: AKUN REAL SIAP DIGUNAKAN!")
            print("=============================================")
            print(f"Email      : {email_user}")
            print(f"Password   : {password_user}")
            print(f"User UID   : {firebase_uid}")
            print("Status     : Terdaftar di Fire Auth & Cloud Firestore")
            print("=============================================\n")
        else:
            print(f"[GAGAL FIRESTORE] Profil gagal disimpan. Status: {firestore_response.status_code}")
            print(f"Detail: {firestore_response.text}")
            
    except Exception as e:
        print(f"[NET ERROR] Gagal menghubungi Cloud Firestore: {str(e)}")

if __name__ == "__main__":
    seed_complete_user_account()