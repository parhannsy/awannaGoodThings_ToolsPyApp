"""
Main App: SalesDataApp
Mengimplementasikan Single Window Architecture dengan memuat form login 
sebagai gerbang masuk sebelum merender layout dashboard utama.
Mendukung penuh siklus Login dan Logout dinamis dalam satu jendela (Single Window),
lengkap dengan umpan balik visual Toast Notification.
"""

import customtkinter as ctk
from pathlib import Path

from infrastructure.config.app_config import AppConfig
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
from presentation.components.shared.toast import Toast  # 🌟 Integrasi komponen Toast


class SalesDataApp:
    """Main application window."""
    
    def __init__(self):
        self.config = AppConfig()
        self.config.ensure_directories()
        
        ctk.set_appearance_mode(self.config.THEME)
        ctk.set_default_color_theme(self.config.COLOR_THEME)
        
        self.root = ctk.CTk()
        self.root.title(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.root.geometry(f"{self.config.APP_WIDTH}x{self.config.APP_HEIGHT}")
        self.root.minsize(900, 600)
        
        # Penampung sesi data user aktif standar industri
        self.session_user = None
        
        # SINGLE WINDOW FLOW: Tampilkan layar login terlebih dahulu saat aplikasi dibuka
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
        
        # 1. Bersihkan panel login dari jendela utama secara total
        self.login_page.pack_forget()
        self.login_page.destroy()
        
        print(f"[SESSION STARTED] Berhasil masuk sebagai: {user_profile['nama']} ({user_profile['role']})")
        
        # 2. Bangun kembali seluruh tata letak dan komponen dashboard utama aplikasi
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()
        
        # 3. Alihkan tampilan langsung ke halaman dashboard bawaan
        self.show_view("dashboard")

        # 🌟 TOAST 1: Berhasil Login (Menggunakan self.root sebagai objek widget master)
        Toast.success(
            master=self.root,
            message=f"Selamat datang kembali, {user_profile.get('nama', 'User')}!"
        )

    def _handle_logout(self):
        """Menghancurkan tampilan dashboard utama dan mengembalikan user ke halaman login."""
        # 1. Bersihkan data sesi user aktif dari memori aplikasi
        self.session_user = None
        
        # 2. Lepas dan hancurkan layout sidebar serta kontainer view dari window root
        if hasattr(self, 'sidebar'):
            self.sidebar.grid_forget()
            self.sidebar.destroy()
            
        if hasattr(self, 'content_frame'):
            self.content_frame.grid_forget()
            self.content_frame.destroy()
            
        print("[SESSION CLOSED] Sesi berhasil ditutup secara aman. Kembali ke layar login.")
        
        # 3. Panggil ulang komponen halaman login ke dalam single window utama yang sama
        self._show_login_screen()

        # 🌟 TOAST 2: Berhasil Logout
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
            on_navigate=self.show_view,
            on_logout=self._handle_logout,  # Mengirim callback logout ke komponen sidebar
            app_name=self.config.APP_NAME
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def _setup_views(self):
        self.views = {}
        
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Registrasi seluruh modul view yang tersedia di aplikasi
        self.views["dashboard"] = DashboardView(self.content_frame)
        self.views["regional_summary"] = RegionalSummaryView(self.content_frame)
        self.views["rate_zonasi"] = RateZonasiView(self.content_frame)
        self.views["transformer"] = TransformerView(self.content_frame)
        self.views["performance"] = PerformanceView(self.content_frame)
        self.views["history"] = HistoryView(self.content_frame)
        self.views["firebase_status"] = FirebaseStatusView(self.content_frame)
        self.views["produk_index"] = ProdukIndexView(self.content_frame)
        self.views["keuangan_index"] = KeuanganIndexView(self.content_frame)

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove()
    
    def show_view(self, view_name: str):
        for view in self.views.values():
            view.grid_remove()
        
        if view_name in self.views:
            self.views[view_name].grid()
            self.views[view_name].on_show()
            self.sidebar.set_active(view_name)
    
    def run(self):
        self.root.mainloop()