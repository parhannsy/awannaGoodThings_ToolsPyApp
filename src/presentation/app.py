"""
Main App: SalesDataApp
Mengimplementasikan Single Window Architecture dengan Dynamic Role-Based Access Control (RBAC).
Hanya memuat view dan menu yang diizinkan sesuai hak akses role aktif.
"""

import customtkinter as ctk
from pathlib import Path

from infrastructure.config.app_config import AppConfig
from infrastructure.config.role_config import get_allowed_menu_for_role, ROLE_ACCESS_MATRIX # 🌟 Import RBAC Engine
from presentation.components.side_bar import Sidebar
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
from presentation.components.shared.toast import Toast


class SalesDataApp:
    """Main application window with Dynamic RBAC routing."""
    
    def __init__(self):
        self.config = AppConfig()
        self.config.ensure_directories()
        
        ctk.set_appearance_mode(self.config.THEME)
        ctk.set_default_color_theme(self.config.COLOR_THEME)
        
        self.root = ctk.CTk()
        self.root.title(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.root.geometry(f"{self.config.APP_WIDTH}x{self.config.APP_HEIGHT}")
        self.root.minsize(900, 600)
        
        self.session_user = None
        
        # Tampilkan layar login terlebih dahulu saat aplikasi dibuka
        self._show_login_screen()
    
    def _show_login_screen(self):
        """Membuat dan menampilkan panel login memenuhi jendela utama."""
        self.login_page = LoginView(
            master=self.root, 
            on_login_success_callback=self._handle_login_success
        )
        self.login_page.pack(fill="both", expand=True)

    def _handle_login_success(self, user_profile: dict):
        """Callback yang dipicu secara otomatis saat autentikasi Firebase sukses."""
        self.session_user = user_profile
        
        self.login_page.pack_forget()
        self.login_page.destroy()
        
        print(f"[SESSION STARTED] Berhasil masuk sebagai: {user_profile['nama']} ({user_profile['role']})")
        
        # 🌟 LOGIKA RBAC: Ambil struktur menu yang valid khusus untuk role ini
        self.allowed_menu_groups = get_allowed_menu_for_role(user_profile['role'])
        
        # Bangun kembali seluruh tata letak dan komponen dashboard utama aplikasi
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()
        
        # Alihkan tampilan langsung ke halaman dashboard bawaan
        self.show_view("dashboard")

        Toast.success(
            master=self.root,
            message=f"Selamat datang kembali, {user_profile.get('nama', 'User')}!"
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
        # 🌟 PERBAIKAN: Melempar daftar menu tersaring (self.allowed_menu_groups) ke Sidebar
        self.sidebar = Sidebar(
            master=self.root,
            menu_groups=self.allowed_menu_groups,
            on_navigate=self.show_view,
            on_logout=self._handle_logout,
            app_name=self.config.APP_NAME
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def _setup_views(self):
        """🌟 OPTIMASI RE-ARCHITECTING: Hanya menginstansiasi view yang diizinkan oleh Role."""
        self.views = {}
        
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Map blueprint instansiasi seluruh view kelas
        view_blueprints = {
            "dashboard": DashboardView,
            "regional_summary": RegionalSummaryView,
            "rate_zonasi": RateZonasiView,
            "transformer": TransformerView,
            "performance": PerformanceView,
            "history": HistoryView,
            "firebase_status": FirebaseStatusView,
            "produk_index": ProdukIndexView,
            "keuangan_index": KeuanganIndexView
        }
        
        # Ambil daftar ID yang diizinkan untuk role ini
        user_role = self.session_user['role'].strip().lower()
        allowed_ids = ROLE_ACCESS_MATRIX.get(user_role, ["dashboard"])
        
        # 🌟 LAZY LAUNCHER: Instansiasi HANYA view yang diperbolehkan oleh hak akses role
        for view_id, view_class in view_blueprints.items():
            if view_id in allowed_ids:
                self.views[view_id] = view_class(self.content_frame)
                self.views[view_id].grid(row=0, column=0, sticky="nsew")
                self.views[view_id].grid_remove()
    
    def show_view(self, view_name: str):
        for view in self.views.values():
            view.grid_remove()
        
        if view_name in self.views:
            self.views[view_name].grid()
            self.views[view_name].on_show()
            self.sidebar.set_active(view_name)
    
    def run(self):
        self.root.mainloop()