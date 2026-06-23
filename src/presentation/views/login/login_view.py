"""
LoginView
Mendukung arsitektur Single Window dengan penanganan dependensi konfigurasi 
yang defensif untuk mencegah AttributeError akibat kesalahan tipe data runtime.
"""

import threading
import customtkinter as ctk
from tkinter import messagebox
from infrastructure.persistence.firebase_auth_impl import FirebaseAuthRepository
from infrastructure.config.app_config import AppConfig


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success_callback, **kwargs):
        # Inisialisasi sebagai Frame, sewarna dengan background utama dashboard
        super().__init__(master, fg_color="#111827", corner_radius=0, **kwargs)
        
        self.on_login_success = on_login_success_callback
        self.auth_repo = FirebaseAuthRepository()
        
        # 🌟 PERBAIKAN DEFENSIF: Validasi ketat tipe data master.config (Atasi AttributeError 'function')
        self.app_config = None
        if hasattr(master, 'config'):
            # Jika master.config adalah fungsi/callable (bukan instansi objek), kita eksekusi fungsinya
            if callable(master.config):
                try:
                    self.app_config = master.config()
                except Exception:
                    self.app_config = AppConfig()
            else:
                self.app_config = master.config
        
        # Fallback terakhir jika tetap gagal mendapatkan objek valid
        if not self.app_config or isinstance(self.app_config, type) or not hasattr(self.app_config, 'get_last_login_email'):
            self.app_config = AppConfig()
            # Pastikan direktori cache siap jika menggunakan instansi fallback baru
            self.app_config.ensure_directories()
            
        self._setup_ui()

    def _setup_ui(self):
        # Central Login Card tetap diletakkan di tengah menggunakan place
        self.card = ctk.CTkFrame(self, fg_color="#1F2937", corner_radius=12, width=380, height=450)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Title & Subtitle App
        self.title_label = ctk.CTkLabel(
            self.card, 
            text="Awanna media's Tools", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=(40, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.card, 
            text="Sales Data Workspace Sign In", 
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Input Email
        self.email_label = ctk.CTkLabel(self.card, text="Email Address", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.email_label.pack(anchor="w", padx=30, pady=(10, 2))
        
        self.entry_email = ctk.CTkEntry(self.card, width=320, height=35, fg_color="#374151", border_color="#4B5563")
        self.entry_email.pack(padx=30)
        
        # Ambil dari cache lokal melalui penampung config yang sudah divalidasi aman
        last_email = self.app_config.get_last_login_email()
        if last_email:
            self.entry_email.insert(0, last_email)

        # Input Password
        self.password_label = ctk.CTkLabel(self.card, text="Password", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.password_label.pack(anchor="w", padx=30, pady=(15, 2))
        
        self.entry_password = ctk.CTkEntry(self.card, width=320, height=35, show="*", fg_color="#374151", border_color="#4B5563")
        self.entry_password.pack(padx=30)

        # Button Sign In
        self.btn_login = ctk.CTkButton(
            self.card, 
            text="Sign In", 
            command=self.handle_login_click,
            width=320,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981", 
            hover_color="#059669"
        )
        self.btn_login.pack(pady=(40, 10))

    def handle_login_click(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()

        if not email or not password:
            messagebox.showwarning("Peringatan", "Email dan Password wajib diisi!")
            return

        self.btn_login.configure(state="disabled", text="Authenticating...")
        threading.Thread(target=self._login_worker, args=(email, password), daemon=True).start()

    def _login_worker(self, email, password):
        user_profile = self.auth_repo.login_user(email, password)
        
        if user_profile:
            if not user_profile["isActive"]:
                self.after(0, lambda: self.btn_login.configure(state="normal", text="Sign In"))
                self.after(0, lambda: messagebox.showerror("Akses Ditolak", "Akun Anda saat ini dinonaktifkan."))
                return
            
            # Simpan email ke dalam persistent storage
            self.app_config.save_last_login_email(email)
            
            # Pemicuan sukses
            self.after(0, lambda: self.on_login_success(user_profile))
        else:
            self.after(0, lambda: self.btn_login.configure(state="normal", text="Sign In"))
            self.after(0, lambda: messagebox.showerror("Gagal Autentikasi", "Email atau Password salah."))