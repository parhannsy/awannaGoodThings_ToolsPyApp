"""
View: UserManagementIndexView
Orkestrator utama halaman manajemen user & tim offline memanfaatkan layout Tab modern.
Fix Safe Layout: Menghilangkan internal padding bawaan CTkTabview via grid_configure (Bebas ValueError Crash).
"""

import threading
import customtkinter as ctk
from presentation.components.shared.page_header import PageHeader
from presentation.components.user_management.user_action_bar import UserActionBar
from presentation.components.user_management.user_summary_card import UserSummaryCard
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
        # 1. Menggunakan Shared PageHeader (Sejajar sempurna)
        self.header = PageHeader(
            master=self,
            title="Manajemen Karyawan & Tim",
            subtitle="Kelola akuntabilitas login staff aktif dan monitoring database personil tim internal."
        )
        
        # 2. Komponen Bilah Aksi atas (Search, Tambah, Edit Toggle)
        self.action_bar = UserActionBar(
            master=self,
            on_search_callback=self._handle_search,
            on_add_click_callback=self._open_add_form_router,
            on_edit_toggle_callback=self._handle_edit_toggle
        )
        self.action_bar.pack(fill="x", padx=5, pady=(0, 15))

        # 3. SUMMARY CARD (Komponen hasil pemisahan modular rapi)
        self.summary_card = UserSummaryCard(master=self)
        self.summary_card.pack(fill="x", padx=5, pady=(0, 10))

        # 4. KONFIGURASI TAB VIEW STYLE BROWSER (LEFT ALIGNED)
        self.tab_channels = ctk.CTkTabview(
            self, 
            fg_color="transparent", 
            corner_radius=8,
            segmented_button_selected_color="#3B82F6",         
            segmented_button_selected_hover_color="#2563EB",   
            segmented_button_unselected_color="#1F2937",       
            segmented_button_unselected_hover_color="#374151"  
        )
        self.tab_channels.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Penamaan minimalis murni sesuai permintaan
        self.tab_staff = self.tab_channels.add("Staff")
        self.tab_team = self.tab_channels.add("Tim")
        
        # Kustomisasi Font pada tombol pilihan Tab agar lebih tegas profesional
        self.tab_channels._segmented_button.configure(
            font=ctk.CTkFont(size=13, weight="bold")
        )
        
        # Memaksa Grid Tkinter internal memarkir tombol segmen ke Sisi Kiri
        self.tab_channels._segmented_button.grid_configure(sticky="w")
        
        # 🌟 SOLUSI AMAN FIX INDENTATION (ANTI CRASH):
        # Alih-alih mengonfigurasi frame tab, kita atur kolom grid utamanya agar meregang penuh
        self.tab_channels.tab("Staff").grid_columnconfigure(0, weight=1)
        self.tab_channels.tab("Tim").grid_columnconfigure(0, weight=1)
        
        # 5. Komponen Tabel Data Karyawan (Staff)
        self.user_table = UserTable(
            master=self.tab_staff,
            on_toggle_status_callback=self._handle_toggle_user_status,
            on_edit_row_callback=self._open_user_edit_dialog,
            on_change_password_callback=self._open_change_password_dialog
        )
        # 🌟 Mengatur pemaksaan layout padding langsung pada level penempatan widget tabel
        self.user_table.pack(fill="both", expand=True, padx=0, pady=(5, 0))
        
        # 6. Komponen Tabel Data Tim Offline (Tim)
        self.team_table = TeamTable(
            master=self.tab_team,
            on_edit_row_callback=self._open_team_edit_dialog
        )
        # 🌟 Mengatur pemaksaan layout padding langsung pada level penempatan widget tabel
        self.team_table.pack(fill="both", expand=True, padx=0, pady=(5, 0))

        # 🌟 TRICK FINISH FIXING: Memaksa container pembungkus internal milik CustomTkinter mengosongkan padding-nya
        # Ini adalah cara legal memanipulasi posisi penempatan grid internal yang disetujui Tkinter engine
        for tab_name in ["Staff", "Tim"]:
            for child in self.tab_channels.tab(tab_name).winfo_children():
                child.pack_configure(padx=0)

    # ============================================================
    # METHOD: Handler untuk Toggle Status User (isActive boolean)
    # ============================================================
    def _handle_toggle_user_status(self, user_data: dict):
        """
        Menangani perubahan status aktif/nonaktif user.
        Field Firebase: isActive (boolean).
        Menggunakan user_service.update_user_profile() sesuai UserRepositoryPort.
        """
        id_user = user_data.get("idUser") or user_data.get("uid")
        if not id_user:
            Toast.error(
                master=self.winfo_toplevel(),
                message="ID user tidak ditemukan, tidak dapat mengubah status."
            )
            return

        # Ambil nilai isActive saat ini (default True jika tidak ada)
        current_is_active = bool(user_data.get("isActive", True))
        new_is_active = not current_is_active  # Toggle boolean

        try:
            # Panggil method sesuai UserRepositoryPort: update_user_profile(id_user, profile_data)
            profile_data = {"isActive": new_is_active}
            self.user_service.update_user_profile(id_user, profile_data)

            status_label = "AKTIF" if new_is_active else "NONAKTIF"
            Toast.success(
                master=self.winfo_toplevel(),
                message=f"Status user berhasil diubah menjadi {status_label}."
            )
            self.load_data()  # Refresh data setelah update

        except Exception as e:
            Toast.error(
                master=self.winfo_toplevel(),
                message=f"Gagal mengubah status user: {str(e)}"
            )

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
        
        # Jalankan kalkulasi summary terpisah
        self._update_totals_card()

    def _update_totals_card(self):
        total_staff = len(self.cached_users)
        total_teams = len(self.cached_teams)
        total_sdm = total_staff + total_teams

        # Breakdown staff per role
        role_counts = {}
        for u in self.cached_users:
            r = str(u.get('role','')).strip().lower() or 'unknown'
            role_counts[r] = role_counts.get(r, 0) + 1

        staff_breakdown_lines = [f"{role}: {cnt}" for role, cnt in role_counts.items()]

        # Breakdown team per role_tim
        team_role_counts = {}
        for t in self.cached_teams:
            r = str(t.get('role_tim','')).strip().lower() or 'unknown'
            team_role_counts[r] = team_role_counts.get(r, 0) + 1

        team_breakdown_lines = [f"{role}: {cnt}" for role, cnt in team_role_counts.items()]

        # Delegasikan pembaruan teks langsung ke metode internal komponen Summary Card
        self.summary_card.update_statistics(
            total_sdm=total_sdm,
            total_staff=total_staff,
            total_teams=total_teams,
            staff_breakdown=staff_breakdown_lines,
            team_breakdown=team_breakdown_lines
        )

    def _handle_edit_toggle(self, enabled: bool):
        # Perintahkan tabel untuk menampilkan kolom aksi edit melalui API method
        if hasattr(self.user_table, 'set_show_actions'):
            self.user_table.set_show_actions(enabled)
        else:
            self.user_table._show_actions = enabled

        if hasattr(self.team_table, 'set_show_actions'):
            self.team_table.set_show_actions(enabled)
        else:
            self.team_table._show_actions = enabled

        self._apply_filter_and_render()

    def _open_user_edit_dialog(self, user_data: dict):
        UserFormDialog(
            master=self.winfo_toplevel(),
            user_data=user_data,
            account_service=self.account_service,
            user_service=self.user_service,
            on_success_callback=self._on_user_action_success
        )

    def _open_team_edit_dialog(self, team_data: dict):
        TeamFormDialog(
            master=self.winfo_toplevel(),
            user_service=self.user_service,
            existing_team=team_data,
            on_success_callback=self._on_team_action_success
        )

    def _open_change_password_dialog(self, user_data: dict):
        from presentation.components.user_management.change_password_dialog import ChangePasswordDialog

        email = user_data.get('email')
        role = str(user_data.get('role', '')).strip().lower()
        if not email:
            Toast.error(master=self.winfo_toplevel(), message="User tidak memiliki email untuk reset password.")
            return

        if role not in ("mentor", "admin"):
            Toast.error(master=self.winfo_toplevel(), message="Reset password hanya diperbolehkan untuk akun Mentor atau Admin.")
            return

        ChangePasswordDialog(master=self.winfo_toplevel(), account_service=self.account_service, email=email)

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