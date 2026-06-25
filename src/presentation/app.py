"""
Main App: SalesDataApp
Mengimplementasikan Single Window Architecture dengan True Lazy Loading & 
Dynamic Role-Based Access Control (RBAC). Objek halaman hanya dibuat saat diakses.
"""

import customtkinter as ctk

from infrastructure.config.role_config import get_allowed_menu_for_role, ROLE_ACCESS_MATRIX
from presentation.components.side_bar import Sidebar
from presentation.dependency_container import create_presentation_services
from presentation.views.dashboard_view import DashboardView
from presentation.views.keuangan.index import KeuanganIndexView
from presentation.views.produk.index import ProdukIndexView
from presentation.views.tools.rate_zonasi_view import RateZonasiView
from presentation.views.tools.regional_summary_view import RegionalSummaryView
from presentation.views.tools.transformer_view import TransformerView
from presentation.views.tools.performance_view import PerformanceView
from presentation.views.history_view import HistoryView
from presentation.views.firebase_status.firebase_status_view import FirebaseStatusView
from presentation.views.login.login_view import LoginView
from presentation.views.user_management.index import UserManagementIndexView
from presentation.components.shared.toast import Toast


class SalesDataApp:
    """Main application window with Dynamic RBAC routing and Lazy View Initialization."""
    
    def __init__(self, app_config=None, services=None):
        self.config = app_config or self._build_default_config()
        self.config.ensure_directories()

        ctk.set_appearance_mode(self.config.THEME)
        ctk.set_default_color_theme(self.config.COLOR_THEME)
        
        self.root = ctk.CTk()
        self.root.title(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.root.geometry(f"{self.config.APP_WIDTH}x{self.config.APP_HEIGHT}")
        self.root.minsize(900, 600)
        self.root.after(0, self._maximize_window)

        self.services = services or create_presentation_services()
        self.session_user = None
        self._show_login_screen()

    def _build_default_config(self):
        from infrastructure.config.app_config import AppConfig
        return AppConfig()
    
    def _show_login_screen(self):
        """Membuat dan menampilkan panel login memenuhi jendela utama."""
        self.login_page = LoginView(
            master=self.root,
            account_service=self.services["account_service"],
            app_config=self.config,
            on_login_success_callback=self._handle_login_success
        )
        self.login_page.pack(fill="both", expand=True)

    def _maximize_window(self):
        """Maximalkan jendela aplikasi setelah root dibuat."""
        try:
            self.root.state("zoomed")
            self.root.attributes("-zoomed", True)
        except Exception as e:
            print(f"[WINDOW] Gagal memaksimalkan jendela: {e}")

    def _handle_login_success(self, user_profile: dict):
        """Callback otomatis saat login sukses. Mendukung interupsi CompleteProfileView."""
        self.session_user = user_profile
        
        # 1. Bersihkan panel login dari jendela utama secara total
        self.login_page.pack_forget()
        self.login_page.destroy()
        
        print(f"[SESSION STARTED] Berhasil login sebagai: {user_profile.get('email')} (Role: {user_profile.get('role')})")
        
        # 🌟 LOGIKA UTAMA INTERUPSI: Deteksi boolean dengan konversi defensif
        is_complete = user_profile.get("isProfileComplete", False)
        if str(is_complete).lower() == 'true':
            is_complete = True

        if self._needs_profile_completion(user_profile):
            profile_name = str(user_profile.get("nama", "")).strip()
            print(f"[PROFILE INCOMPLETE] Mengalihkan {user_profile.get('email')} ke halaman pengisian profil. isProfileComplete={is_complete}, nama='{profile_name}'")

            Toast.info(
                master=self.root,
                message="Profil Anda belum lengkap. Silakan lengkapi data tambahan sebelum masuk ke dashboard."
            )

            from presentation.views.login.complete_profile import CompleteProfileView

            self.complete_profile_page = CompleteProfileView(
                master=self.root,
                session_user=self.session_user,
                user_service=self.services["user_service"],
                on_completion_success=self._handle_profile_completion_finish
            )
            self.complete_profile_page.pack(fill="both", expand=True)
            return

        # 2. ALUR NORMAL: Jika profil sudah lengkap, bangun layout workspace
        self._build_main_workspace()

    def _handle_profile_completion_finish(self, completed_user_profile: dict):
        """Dipanggil setelah pengguna sukses menyelesaikan seluruh proses profil lengkap."""
        self.session_user = completed_user_profile
        
        # Bersihkan halaman interupsi dari window utama
        self.complete_profile_page.pack_forget()
        self.complete_profile_page.destroy()
        
        print(f"[PROFILE COMPLETED] Profil berhasil diperbarui untuk: {self.session_user.get('nama')}")
        
        self._build_main_workspace()

    def _needs_profile_completion(self, user_profile: dict) -> bool:
        required_fields = [
            "nama",
            "panggilan",
            "alamat",
            "nohp",
            "bank",
            "nomor_rekening",
        ]
        return any(not str(user_profile.get(field, "")).strip() for field in required_fields)

    def _build_main_workspace(self):
        """Helper internal untuk membangun infrastruktur layout, sidebar, dan views."""
        # Ekstraksi dan sanitasi nama role
        user_role = str(self.session_user.get('role', 'advertiser')).strip().lower()
        self.allowed_menu_groups = get_allowed_menu_for_role(user_role)
        
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()
        
        self.show_view("dashboard")

        Toast.success(
            master=self.root,
            message=f"Selamat datang kembali, {self.session_user.get('nama', 'User')}!"
        )

    def _handle_logout(self):
        """Menghancurkan tampilan dashboard utama dan mengembalikan user ke halaman login."""
        self.session_user = None
        
        if hasattr(self, 'sidebar'):
            self.sidebar.grid_forget()
            self.sidebar.destroy()
            
        if hasattr(self, 'content_frame'):
            self.content_frame.grid_forget()
            self.content_frame.destroy()
            
        print("[SESSION CLOSED] Sesi berhasil ditutup secara aman. Kembali ke layar login.")
        self._show_login_screen()

        Toast.success(
            master=self.root,
            message="Anda telah berhasil keluar dari sesi sistem."
        )

    def _setup_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def _setup_sidebar(self):
        self.sidebar = Sidebar(
            master=self.root,
            menu_groups=self.allowed_menu_groups,
            on_navigate=self.show_view,
            on_logout=self._handle_logout,
            app_name=self.config.APP_NAME
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def _setup_views(self):
        """🌟 PERBAIKAN ARSITEKTUR: Menerapkan True Lazy Loading Menggunakan Lambda Blueprint."""
        self.views = {}
        
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        user_role = str(self.session_user.get('role', 'advertiser')).strip().lower()
        self.allowed_ids = ROLE_ACCESS_MATRIX.get(user_role, ["dashboard"])
        
        self.view_blueprints = {
            "dashboard": lambda master: DashboardView(master, app_config=self.config),
            "regional_summary": lambda master: RegionalSummaryView(master),
            "rate_zonasi": lambda master: RateZonasiView(master),
            "transformer": lambda master: TransformerView(master),
            "performance": lambda master: PerformanceView(master),
            "history": lambda master: HistoryView(master),
            "firebase_status": lambda master: FirebaseStatusView(master, firebase_status_service=self.services["firebase_status_service"]),
            "produk_index": lambda master: ProdukIndexView(master),
            "keuangan_index": lambda master: KeuanganIndexView(master),
            "user_management_index": lambda master: UserManagementIndexView(master, user_service=self.services["user_service"], account_service=self.services["account_service"])
        }
    
    def show_view(self, view_name: str):
        """Melahirkan objek view secara dinamis dan aman saat menu diklik."""
        if view_name not in self.allowed_ids:
            print(f"[SECURITY ALERT] Hak akses ditolak untuk halaman: {view_name}")
            return

        for view in self.views.values():
            view.grid_remove()
        
        if view_name not in self.views and view_name in self.view_blueprints:
            print(f"[LAZY ENGINE] Menginstansiasi halaman baru: '{view_name}'")
            self.views[view_name] = self.view_blueprints[view_name](self.content_frame)
            self.views[view_name].grid(row=0, column=0, sticky="nsew")
        
        if view_name in self.views:
            self.views[view_name].grid()
            
            if hasattr(self.views[view_name], 'on_show'):
                self.views[view_name].on_show()
                
            self.sidebar.set_active(view_name)
    
    def run(self):
        self.root.mainloop()