"""
Component: UserFormDialog
Modal dialog pop-up untuk operasi Create (Tambah) dan Update (Edit) data user.
Mentor hanya mengisi Email, Password, dan Role. Sesuai arsitektur REST API.
"""

import threading
import customtkinter as ctk
from presentation.components.shared.toast import Toast


class UserFormDialog(ctk.CTkToplevel):
    def __init__(self, master, user_data=None, account_service=None, user_service=None, on_success_callback=None):
        super().__init__(master)
        
        self.user_data = user_data  # Jika ada data = EDIT, Jika None = TAMBAH
        self.account_service = account_service
        self.user_service = user_service
        self.on_success = on_success_callback
        
        # Setup Window
        self.title("Form Karyawan" if not user_data else "Edit Karyawan")
        self.geometry("400x420")
        self.resizable(False, False)
        self.configure(fg_color="#1F2937")
        
        # Penanganan fokus window modal
        self.transient(master)
        self.attributes("-topmost", True)
        self.grab_set()
        
        self._setup_ui()
        
        if self.user_data:
            self._load_user_data()

    def _setup_ui(self):
        # Container utama dengan padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Header Label
        title_text = "✨ Tambah Akun Karyawan" if not self.user_data else "📝 Edit Akses Karyawan"
        self.lbl_title = ctk.CTkLabel(
            main_frame, text=title_text, 
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFFFFF"
        )
        self.lbl_title.pack(anchor="w", pady=(0, 20))
        
        # Input: Email
        self.lbl_email = ctk.CTkLabel(main_frame, text="Email Address", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF")
        self.lbl_email.pack(anchor="w", pady=(10, 2))
        self.entry_email = ctk.CTkEntry(
            main_frame, width=350, height=35, placeholder_text="karyawan@awannamedia.com",
            fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF"
        )
        self.entry_email.pack(fill="x")
        
        # Input: Password (Hanya muncul saat TAMBAH akun baru)
        self.lbl_password = ctk.CTkLabel(main_frame, text="Password Account", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF")
        self.lbl_password.pack(anchor="w", pady=(10, 2))
        self.entry_password = ctk.CTkEntry(
            main_frame, width=350, height=35, show="*", placeholder_text="Minimal 6 karakter",
            fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF"
        )
        self.entry_password.pack(fill="x")
        
        # Input: Role Selection Dropdown (Menyesuaikan dengan lowercase matrix)
        self.lbl_role = ctk.CTkLabel(main_frame, text="Role Jabatan", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF")
        self.lbl_role.pack(anchor="w", pady=(10, 2))
        self.combo_role = ctk.CTkComboBox(
            main_frame, 
            values=["advertiser", "mentor", "keuangan", "admin"],
            height=35,
            fg_color="#374151", border_color="#4B5563", button_color="#4B5563", text_color="#FFFFFF"
        )
        self.combo_role.pack(fill="x")
        self.combo_role.set("advertiser")  # Default value standar proyek
        
        # Jika mode edit, sembunyikan password field karena tidak relevan
        if self.user_data:
            self.entry_email.configure(state="disabled")  # Email bersifat Immutable
            self.lbl_password.pack_forget()
            self.entry_password.pack_forget()

        # Action Buttons Container
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        self.btn_cancel = ctk.CTkButton(
            btn_frame, text="Batal", width=110, height=38, 
            fg_color="#4B5563", hover_color="#374151", text_color="white",
            command=self.destroy
        )
        self.btn_cancel.pack(side="left")
        
        self.btn_save = ctk.CTkButton(
            btn_frame, text="Simpan Akun", width=220, height=38,
            fg_color="#10B981", hover_color="#059669", text_color="white",
            command=self._handle_save
        )
        self.btn_save.pack(side="right")

    def _load_user_data(self):
        """Memuat data lama ke komponen input saat mode EDIT."""
        self.entry_email.configure(state="normal")
        self.entry_email.insert(0, self.user_data.get("email", ""))
        self.entry_email.configure(state="disabled")
        
        role_raw = self.user_data.get("role", "advertiser").lower()
        self.combo_role.set(role_raw)

    def _handle_save(self):
        email = self.entry_email.get().strip()
        role = self.combo_role.get().strip().lower()
        
        # Logika Skenario TAMBAH Akun Baru
        if not self.user_data:
            password = self.entry_password.get().strip()
            if not email or not password:
                Toast.error(master=self, message="Kolom Email & Password wajib diisi!")
                return
            if len(password) < 6:
                Toast.error(master=self, message="Password minimal harus 6 karakter!")
                return
            
            self.btn_save.configure(state="disabled", text="Mendaftarkan...")
            threading.Thread(target=self._create_worker, args=(email, password, role), daemon=True).start()
        
        # Logika Skenario EDIT Akun Lama
        else:
            self.btn_save.configure(state="disabled", text="Memperbarui...")
            threading.Thread(target=self._update_worker, args=(role,), daemon=True).start()

    def _create_worker(self, email, password, role):
        """Worker untuk mendaftarkan akun melalui service aplikasi."""
        profile_payload = {
            "email": email,
            "nama": "",
            "panggilan": "",
            "role": role,
            "isActive": True,
            "isProfileComplete": False
        }

        try:
            if not self.account_service:
                raise RuntimeError("Account service belum disuntikkan ke UserFormDialog.")

            self.account_service.create_user_account(email, password, profile_payload)
            self.after(0, self._finalize_success)

        except Exception as e:
            self.after(0, lambda: self.btn_save.configure(state="normal", text="Simpan Akun"))
            self.after(0, lambda: Toast.error(master=self, message=str(e)))

    def _update_worker(self, role):
        """Worker untuk memperbarui role akun di Firestore."""
        # Menyesuaikan mapping key data dari Firestore REST API (idUser / UID)
        id_user = self.user_data.get("idUser") or self.user_data.get("uid")
        
        if not self.user_service:
            self.after(0, lambda: Toast.error(master=self, message="User service belum disuntikkan ke UserFormDialog."))
            return

        success = self.user_service.update_user_profile(id_user, {"role": role})
        if success:
            self.after(0, self._finalize_success)
        else:
            self.after(0, lambda: self.btn_save.configure(state="normal", text="Simpan Akun"))
            self.after(0, lambda: Toast.error(master=self, message="Gagal memperbarui role akun."))

    def _finalize_success(self):
        if self.on_success:
            self.on_success()
        self.destroy()