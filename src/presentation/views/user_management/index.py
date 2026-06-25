"""
View: UserManagementIndexView
Orkestrator utama halaman manajemen user & tim offline memanfaatkan layout Tab modern.
Fix: Mengatur posisi tombol tab merapat ke pojok kiri atas (Left-aligned) layaknya browser tab.
"""

import threading
import customtkinter as ctk
from presentation.components.shared.page_header import PageHeader
from presentation.components.user_management.user_action_bar import UserActionBar
from presentation.components.user_management.user_table import UserTable
from presentation.components.user_management.team_table import TeamTable
from presentation.components.user_management.user_form_dialog import UserFormDialog
from presentation.components.user_management.team_form_dialog import TeamFormDialog
from presentation.components.shared.toast import Toast


class UserManagementIndexView(ctk.CTkFrame):
    def __init__(self, master, user_service, account_service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_service = user_service
        self.account_service = account_service
        self.current_search_query = ""
        
        # State cache data lokal untuk pencarian reaktif multi-tab
        self.cached_users = []
        self.cached_teams = []
        self.users_listener = None
        self.teams_listener = None
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Menggunakan Shared PageHeader
        self.header = PageHeader(
            master=self,
            title="Manajemen Karyawan & Tim",
            subtitle="Kelola akuntabilitas login staff aktif dan monitoring database personil tim internal."
        )
        
        # 2. Komponen Bilah Aksi atas (Search & Tambah)
        self.action_bar = UserActionBar(
            master=self,
            on_search_callback=self._handle_search,
            on_add_click_callback=self._open_add_form_router
        )
        self.action_bar.pack(fill="x", padx=5, pady=(0, 15))
        
        # 3. 🌟 KONFIGURASI TAB VIEW STYLE BROWSER (LEFT ALIGNED)
        self.tab_channels = ctk.CTkTabview(
            self, 
            fg_color="transparent", 
            corner_radius=8,
            segmented_button_selected_color="#3B82F6",         # Warna tab aktif (Biru)
            segmented_button_selected_hover_color="#2563EB",   # Warna hover tab aktif
            segmented_button_unselected_color="#1F2937",       # Warna tab tidak aktif (Gelap)
            segmented_button_unselected_hover_color="#374151"  # Warna hover tab tidak aktif
        )
        self.tab_channels.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Penamaan minimalis murni sesuai permintaan
        self.tab_staff = self.tab_channels.add("Staff")
        self.tab_team = self.tab_channels.add("Tim")
        
        # Kustomisasi Font pada tombol pilihan Tab agar lebih tegas profesional
        self.tab_channels._segmented_button.configure(
            font=ctk.CTkFont(size=13, weight="bold")
        )
        
        # 🌟 TRICK UTAMA: Memaksa Grid Tkinter internal memarkir tombol segmen ke Sisi Barat (West/Kiri)
        # Langkah ini memindahkan tombol tab dari posisi tengah (center) bawaan CTk ke pojok kiri.
        self.tab_channels._segmented_button.grid_configure(sticky="w")
        
        # 4. Komponen Tabel Data Karyawan (Staff)
        self.user_table = UserTable(
            master=self.tab_staff,
            on_toggle_status_callback=self._handle_toggle_user_status
        )
        self.user_table.pack(fill="both", expand=True)
        
        # 5. Komponen Tabel Data Tim Offline (Tim)
        self.team_table = TeamTable(
            master=self.tab_team
        )
        self.team_table.pack(fill="both", expand=True)

    def on_show(self):
        """Lifecycle hook otomatis dari Lazy Loading Engine aplikasi."""
        self._ensure_data_streams()
        self.load_data()

    def load_data(self):
        """Mengambil data dari Firestore REST API secara asinkron."""
        threading.Thread(target=self._fetch_all_data_worker, daemon=True).start()

    def _fetch_all_data_worker(self):
        # Ambil data dari koleksi 'users' dan eliminasi role mentor (Owner)
        raw_users = self.user_service.get_all_users()
        self.cached_users = [u for u in raw_users if str(u.get("role", "")).strip().lower() != "mentor"]
        
        # Ambil data dari koleksi 'teams' melalui handler repositori
        try:
            if hasattr(self.user_service, 'get_all_teams'):
                self.cached_teams = self.user_service.get_all_teams()
            else:
                self.cached_teams = []
        except Exception:
            self.cached_teams = []
            
        # Kembalikan ke UI Thread utama untuk melakukan filter dan render data
        self.after(0, self._apply_filter_and_render)

    def _apply_filter_and_render(self):
        """Menerapkan query pencarian lokal pada cache data ke kedua tabel."""
        q = self.current_search_query.lower()
        
        # Filter data staff aplikasi
        display_users = self.cached_users
        if q:
            display_users = [
                u for u in display_users 
                if q in u.get("nama", "").lower() or q in u.get("email", "").lower()
            ]
            
        # Filter data tim offline (CS / Gudang)
        display_teams = self.cached_teams
        if q:
            display_teams = [
                t for t in display_teams 
                if q in t.get("nama", "").lower() or q in t.get("panggilan", "").lower()
            ]
            
        # Kirim data hasil filter ke visual row renderers masing-masing
        self.user_table.render_rows(display_users)
        self.team_table.render_rows(display_teams)

    def _handle_search(self, query: str):
        self.current_search_query = query
        self._apply_filter_and_render()

    def _open_add_form_router(self):
        """Membuka dialog form pendaftaran yang sesuai dengan konteks tab aktif."""
        active_tab = self.tab_channels.get()
        
        if active_tab == "Staff":
            UserFormDialog(
                master=self.winfo_toplevel(),
                account_service=self.account_service,
                user_service=self.user_service,
                on_success_callback=self._on_user_action_success
            )
        else:
            TeamFormDialog(
                master=self.winfo_toplevel(),
                user_service=self.user_service,
                on_success_callback=self._on_team_action_success
            )

    def _on_user_action_success(self):
        Toast.success(master=self.winfo_toplevel(), message="Data karyawan berhasil disinkronkan!")
        self.load_data()

    def _on_team_action_success(self):
        Toast.success(master=self.winfo_toplevel(), message="Data tim berhasil ditambahkan!")
        self.load_data()

    def _ensure_data_streams(self):
        if self.users_listener is None and hasattr(self.user_service, 'stream_users_data'):
            self.users_listener = self.user_service.stream_users_data(self.load_data)

        if self.teams_listener is None and hasattr(self.user_service, 'stream_teams_data'):
            self.teams_listener = self.user_service.stream_teams_data(self.load_data)

    def _handle_toggle_user_status(self, user: dict):
        """Menangani kebijakan soft delete status aktif karyawan via REST API."""
        current_status = user.get("isActive", True)
        new_status = not current_status
        id_user = user.get("idUser") or user.get("uid")
        
        # Optimistic UI update lokal
        user["isActive"] = new_status
        
        def run_update():
            success = self.user_service.update_user_profile(id_user, {"isActive": new_status})
            if success:
                self.after(0, lambda: Toast.success(master=self.winfo_toplevel(), message=f"Status {user.get('nama', 'User')} berhasil diperbarui."))
            else:
                self.after(0, lambda: Toast.error(master=self.winfo_toplevel(), message="Gagal mengubah status di server."))
            self.after(0, self.load_data)

        threading.Thread(target=run_update, daemon=True).start()