"""
Seeder: SeederTim
Skrip utilitas profesional untuk menanamkan data awal anggota tim offline (CS / Gudang).
Fix: Mengubah struktur payload tanggal dari stringValue menjadi timestampValue (Firestore Timestamp).
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Menambahkan root directory proyek ke sys.path agar module src bisa terbaca
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from infrastructure.config.firebase_config import FirebaseConfig

# Memuat konfigurasi variabel lingkungan (.env)
load_dotenv()

def seed_offline_team_account():
    print("=== MEMULAI PROSES SEEDING DATA TIM OFFLINE ===")
    
    api_key = FirebaseConfig.API_KEY
    project_id = FirebaseConfig.PROJECT_ID
    
    if not api_key or not project_id:
        print("[ERROR] Gagal membaca file .env. Pastikan API KEY dan PROJECT ID sudah terisi.")
        return

    # Alamat Firestore URL dinamis menggunakan struktur konfigurasi proyekmu
    firestore_url = FirebaseConfig.get_firestore_url("teams")
    
    # 🌟 FIX AKURASI DATA: Menggunakan timestampValue agar Google menyimpannya sebagai Timestamp resmi
    firestore_payload = {
        "fields": {
            "nama": {"stringValue": "Toha"},
            "panggilan": {"stringValue": "Toha"},
            "alamat": {"stringValue": "Bojong"},
            "nohp": {"stringValue": "08000000000"},
            "isActive": {"booleanValue": True},
            "tanggal_bergabung": {"timestampValue": "2026-04-15T00:00:00Z"}, # 15 April 2026 sebagai Real Timestamp
            "role_tim": {"stringValue": "customerService"}
        }
    }

    try:
        # Kirimkan API Key sebagai parameter agar dikenali oleh Google API Gateway
        params = {
            "key": api_key
        }
        
        print("[INFO] Menembak data tim Toha ke Cloud Firestore...")
        firestore_response = requests.post(firestore_url, json=firestore_payload, params=params, timeout=10)
        
        if firestore_response.status_code in [200, 201]:
            print("\n=============================================")
            print("🎉 SEEDING TIM BERHASIL: DATA TOHA SUDAH MASUK!")
            print("=============================================")
            print("Nama Tim      : Toha")
            print("Panggilan     : Toha")
            print("Divisi Lini   : GUDANG")
            print("Tipe Data Tgl : FIRESTORE TIMESTAMP (Aman untuk Sorting)")
            print("=============================================\n")
        else:
            print(f"\n[GAGAL FIRESTORE] Data gagal disimpan. Status: {firestore_response.status_code}")
            print(f"Detail Error: {firestore_response.text}")
            
    except Exception as e:
        print(f"\n[NET ERROR] Gagal menghubungi Cloud Firestore: {str(e)}")


if __name__ == "__main__":
    seed_offline_team_account()
