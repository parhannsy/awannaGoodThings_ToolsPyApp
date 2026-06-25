import requests
import json
from infrastructure.config.firebase_config import FirebaseConfig

class FirebaseZonasiRepository:
    def __init__(self):
        self.collection_name = "rate_zonasi_logs"
        self.url = FirebaseConfig.get_firestore_url(self.collection_name)

    def save_analysis(self, wilayah: str, rasio_sukses: float, detail_log: str) -> bool:
        """Menyimpan data analisis zonasi ke Firestore menggunakan REST API"""
        # Proteksi jika API Key belum terisi
        if not FirebaseConfig.API_KEY:
            print("[Error] Firebase API Key tidak dikonfigurasi.")
            return False

        # Payload data disesuaikan dengan format tipe data Firestore REST API
        payload = {
            "fields": {
                "wilayah": {"stringValue": wilayah},
                "rasio_sukses": {"doubleValue": rasio_sukses},
                "detail_log": {"stringValue": detail_log}
            }
        }

        try:
            params = {"key": FirebaseConfig.API_KEY}
            response = requests.post(self.url, json=payload, params=params, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"[Firebase Error] Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"[Network Error] Gagal menghubungi Firebase: {str(e)}")
            return False
