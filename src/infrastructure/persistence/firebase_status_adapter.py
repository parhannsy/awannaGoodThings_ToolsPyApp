"""
Adapter: FirebaseStatusAdapter
Implements Firebase connectivity checks through FirebaseStatusRepository.
"""
import requests
from typing import Tuple
from domain.repositories.firebase_status_repository import FirebaseStatusRepository
from infrastructure.config.firebase_config import FirebaseConfig


class FirebaseStatusAdapter(FirebaseStatusRepository):
    """Adapter untuk mengecek status koneksi Firebase via REST API."""

    def check_connection(self) -> Tuple[bool, str]:
        project_id = FirebaseConfig.PROJECT_ID
        api_key = FirebaseConfig.API_KEY

        if not project_id or not api_key:
            return False, "Konfigurasi Firebase tidak ditemukan.",

        test_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/connection_test"
        try:
            response = requests.get(test_url, params={"key": api_key}, timeout=7)
            if response.status_code in [200, 404]:
                return True, "Terhubung ke Firebase Cloud."
            return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as error:
            return False, str(error)
