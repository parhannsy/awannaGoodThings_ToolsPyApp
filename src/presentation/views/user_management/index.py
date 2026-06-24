"""
View: UserManagementIndexView
Orkestrator utama halaman manajemen user yang mengintegrasikan sub-komponen modular.
Aman dari bocornya akun Mentor (Owner) di list karyawan.
"""

import threading
import customtkinter as ctk
from presentation.components.shared.page_header import PageHeader
from presentation.components.user_management.user_action_bar import UserActionBar
from presentation.components.user_management.user_table import UserTable
from presentation.components.user_management.user_form_dialog import UserFormDialog
from infrastructure.persistence.user_repository import UserRepository
from presentation.components.shared.toast import Toast


class UserManagementIndexView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_repo = UserRepository()
        self.current_search_query = ""
        
        self._setup_ui()

    def _setup_ui(self):
        # Menggunakan Shared PageHeader (Komponen otomatis mem-pack dirinya sendiri)
        self.header = PageHeader(
            master=self,
            title="Manajemen Karyawan",
            subtitle="Kelola hak akses kontrol, registrasi staff baru, dan kebijakan soft delete."
        )
        
        # Komponen Bilah Aksi atas
        self.action_bar = UserActionBar(
            master=self,
            on_search_callback=self._handle_search,
            on_add_click_callback=self._open_add_user_form
        )
        self.action_bar.pack(fill="x", padx=5, pady=(0, 15))
        
        # Komponen Tabel Data utama
        self.user_table = UserTable(
            master=self,
            on_toggle_status_callback=self._handle_toggle_user_status
        )
        self.user_table.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def on_show(self):
        """Lifecycle hook otomatis dari Lazy Loading Engine aplikasi."""
        self.load_data()

    def load_data(self):
        """Mengambil data dari Firestore REST API secara asinkron."""
        threading.Thread(target=self._fetch_and_filter_worker, daemon=True).start()

    def _fetch_and_filter_worker(self):
        raw_users = self.user_repo.get_all_users()
        
        # 🌟 LOGIKA UTAMA: Sembunyikan mutlak semua data ber-role 'mentor'
        filtered_users = [u for u in raw_users if str(u.get("role", "")).strip().lower() != "mentor"]
        
        # Lakukan penyaringan data lokal tambahan jika bilah pencarian aktif
        if self.current_search_query:
            q = self.current_search_query.lower()
            filtered_users = [
                u for u in filtered_users 
                if q in u.get("nama", "").lower() or q in u.get("email", "").lower()
            ]
            
        # Kembalikan ke UI Thread utama untuk merender baris tabel
        self.after(0, lambda: self.user_table.render_rows(filtered_users))

    def _handle_search(self, query: str):
        self.current_search_query = query
        self.load_data()

    def _open_add_user_form(self):
        """Memicu pop-up form pendaftaran akun minimalis."""
        UserFormDialog(
            master=self.winfo_toplevel(), 
            on_success_callback=self._on_user_action_success
        )

    def _on_user_action_success(self):
        Toast.success(master=self.winfo_toplevel(), message="Data karyawan berhasil disinkronkan!")
        self.load_data()

    def _handle_toggle_user_status(self, user: dict):
        """Menangani kebijakan soft delete status aktif karyawan via REST API."""
        current_status = user.get("isActive", True)
        new_status = not current_status
        id_user = user.get("idUser") or user.get("uid")
        
        # Optimistic UI update lokal
        user["isActive"] = new_status
        
        def run_update():
            success = self.user_repo.update_user_profile(id_user, {"isActive": new_status})
            if success:
                self.after(0, lambda: Toast.success(master=self.winfo_toplevel(), message=f"Status {user.get('nama', 'User')} berhasil diperbarui."))
            else:
                self.after(0, lambda: Toast.error(master=self.winfo_toplevel(), message="Gagal mengubah status di server."))
            self.after(0, self.load_data)

        threading.Thread(target=run_update, daemon=True).start()