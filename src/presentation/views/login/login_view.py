"""
LoginView
Menangani proses interaksi UI untuk autentikasi pengguna.
Terintegrasi langsung dengan FirebaseAuthRepository REST API dan kebijakan Soft Delete.
"""

import threading
import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    def __init__(self, master, account_service, app_config=None, on_login_success_callback=None, **kwargs):
        super().__init__(master, fg_color="#111827", corner_radius=0, **kwargs)

        self.on_login_success = on_login_success_callback
        self.account_service = account_service
        self.app_config = app_config
        self._ensure_config()
        self._setup_ui()

    def _ensure_config(self):
        if self.app_config is None or not hasattr(self.app_config, 'get_last_login_email'):
            raise RuntimeError("LoginView requires a valid app_config instance.")
        if hasattr(self.app_config, 'ensure_directories'):
            self.app_config.ensure_directories()

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
        
        self.entry_email = ctk.CTkEntry(self.card, width=320, height=35, fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_email.pack(padx=30)
        
        # Ambil dari cache lokal melalui penampung config yang sudah divalidasi aman
        last_email = self.app_config.get_last_login_email()
        if last_email:
            self.entry_email.insert(0, last_email)

        # Input Password
        self.password_label = ctk.CTkLabel(self.card, text="Password", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.password_label.pack(anchor="w", padx=30, pady=(15, 2))
        
        self.entry_password = ctk.CTkEntry(self.card, width=320, height=35, show="*", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
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

        from presentation.components.shared.toast import Toast
        if not email or not password:
            Toast.error(master=self.winfo_toplevel(), message="Email dan Password wajib diisi!")
            return

        self.btn_login.configure(state="disabled", text="Authenticating...")
        threading.Thread(target=self._login_worker, args=(email, password), daemon=True).start()

    def _login_worker(self, email, password):
        """
        Worker thread asinkron yang memanfaatkan fungsi pemanggilan internal 
        dari FirebaseAuthRepository secara efisien tanpa pembacaan ganda.
        """
        from presentation.components.shared.toast import Toast
        try:
            # 1. Panggil fungsi service akun yang sudah dibungkus dari infrastruktur
            user_profile = self.account_service.login_user(email, password)
            
            # Jika kredensial salah atau network bermasalah, service mengembalikan None
            if not user_profile:
                raise ValueError("Email atau Password salah, atau gagal terhubung ke server.")
            
            # 2. INTERUPSI POLICY: Cek Kebijakan Soft Delete (isActive == False)
            # Nilai diambil dari key 'isActive' hasil parsing repositorimu
            if not user_profile.get("isActive", True):
                print(f"[SECURITY CONTROL] Login ditolak. Akun {email} berstatus NONAKTIF.")
                
                self.after(0, lambda: self.btn_login.configure(state="normal", text="Sign In"))
                self.after(0, lambda: Toast.error(
                    master=self.winfo_toplevel(),
                    message="Ups, akunmu dinonaktifkan. Silakan hubungi Mentor atau Admin"
                ))
                return

            # Pastikan minimal data profile tersedia untuk alur complete profile
            user_profile.setdefault("idUser", "")
            user_profile.setdefault("isProfileComplete", False)
            user_profile.setdefault("nama", "")

            # 3. Cache email jika sukses dan alirkan data user ke Main App
            try:
                if hasattr(self.app_config, 'save_last_login_email'):
                    self.app_config.save_last_login_email(email)
                elif hasattr(self.app_config, 'set_last_login_email'):
                    self.app_config.set_last_login_email(email)
            except Exception:
                pass
                
            self.after(0, lambda: self.on_login_success(user_profile))
            
        except Exception as e:
            error_msg = str(e)
            print(f"[LOGIN CRITICAL ERROR] Detail kegagalan: {error_msg}")
            
            self.after(0, lambda: self.btn_login.configure(state="normal", text="Sign In"))
            self.after(0, lambda: Toast.error(
                master=self.winfo_toplevel(), 
                message=f"Login Gagal: {error_msg}"
            ))