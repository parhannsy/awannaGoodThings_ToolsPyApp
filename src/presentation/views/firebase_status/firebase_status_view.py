"""
FirebaseStatusView
Halaman khusus untuk mengecek status integrasi ke Firebase.
Memanfaatkan adaptasi fleksibilitas baru dari BasePageView.
"""

import threading
import customtkinter as ctk
import requests
from src.presentation.views.base.base_page_view import BasePageView
from src.infrastructure.config.firebase_config import FirebaseConfig

class FirebaseStatusView(BasePageView):
    PAGE_TITLE = "Firebase Connectivity Status"
    OUTPUT_TITLE = "Log Detail Koneksi Server"
    
    # KUNCI: Matikan sistem Excel otomatis khusus untuk halaman ini
    REQUIRES_EXCEL_INPUT = False
    HAS_EXCEL_EXPORT = False

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.check_connection()

    def _setup_custom_input(self, parent):
        """Implementasi Hook Input khusus Status Checker"""
        self.control_card = ctk.CTkFrame(parent, corner_radius=8, height=60)
        self.control_card.pack(fill="x", pady=(0, 10))

        self.status_indicator = ctk.CTkLabel(
            self.control_card, 
            text="● Memeriksa Jaringan...", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="orange"
        )
        self.status_indicator.pack(side="left", padx=15, pady=15)

        self.btn_recheck = ctk.CTkButton(
            self.control_card, 
            text="🔄 Cek Ulang Koneksi", 
            command=self.check_connection,
            width=120
        )
        self.btn_recheck.pack(side="right", padx=15, pady=15)

    def _setup_custom_output(self, parent):
        """Implementasi Hook Output khusus Terminal Log"""
        self.log_terminal = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Courier", size=12),
            fg_color="#1E1E1E",
            text_color="#A9DFBF"
        )
        self.log_terminal.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_terminal.configure(state="disabled")

    def check_connection(self):
        self.btn_recheck.configure(state="disabled")
        self.status_indicator.configure(text="● Menghubungi Firebase...", text_color="orange")
        self._write_to_log("=== MEMULAI DIAGNOSIS KONEKSI FIREBASE ===\n")
        threading.Thread(target=self._network_worker, daemon=True).start()

    def _network_worker(self):
        project_id = FirebaseConfig.PROJECT_ID
        api_key = FirebaseConfig.API_KEY
        
        self._write_to_log(f"[INFO] Mencoba ping ke Project ID: {project_id}\n")
        
        if not project_id or not api_key:
            self._update_ui_status(False, "[ERROR] Konfigurasi buntu. File .env tidak ditemukan.\n")
            return

        # 🌟 PERBAIKAN: Mengubah nama koleksi dari '__connection_test__' menjadi 'connection_test'
        # Nama ini aman dari aturan reserved word milik Google Firestore
        test_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/connection_test"
        
        try:
            params = {"key": api_key}
            response = requests.get(test_url, params=params, timeout=7)
            log_detail = f"[HTTP STATUS] {response.status_code}\n[RESPONSE]\n{response.text}\n"
            
            # HTTP 200 (jika koleksi ada data) atau 404 (jika koleksi masih kosong) 
            # Keduanya valid membuktikan autentikasi API Key berhasil menembus server Google.
            if response.status_code in [200, 404]:
                self._update_ui_status(True, log_detail + "[SUKSES] Terhubung ke Firebase Cloud.\n")
            else:
                self._update_ui_status(False, log_detail + "[GAGAL] Server menolak autentikasi.\n")
        except Exception as e:
            self._update_ui_status(False, f"[NET ERROR] Kesalahan: {str(e)}\n")

    def _write_to_log(self, text: str):
        self.log_terminal.configure(state="normal")
        self.log_terminal.insert("end", text)
        self.log_terminal.see("end")
        self.log_terminal.configure(state="disabled")

    def _update_ui_status(self, is_success: bool, final_log: str):
        self._write_to_log(final_log)
        self._write_to_log("=== DIAGNOSIS SELESAI ===\n\n")
        
        if is_success:
            self.status_indicator.configure(text="● Terhubung ke Firebase", text_color="#2ECC71")
        else:
            self.status_indicator.configure(text="● Koneksi Terputus / Error", text_color="#E74C3C")
        self.btn_recheck.configure(state="normal")