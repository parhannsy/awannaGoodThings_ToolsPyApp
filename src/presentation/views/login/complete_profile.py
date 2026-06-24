"""
View: CompleteProfileView
Halaman interupsi berlayar penuh yang memaksa pengguna baru untuk melengkapi 
data profil mereka (Nama Lengkap) saat pertama kali login ke dalam sistem.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from infrastructure.persistence.user_repository import UserRepository
from presentation.components.shared.toast import Toast  # Sinkronisasi komponen toast


class CompleteProfileView(ctk.CTkFrame):
    def __init__(self, master, session_user: dict, on_completion_success: callable, **kwargs):
        # Tampilan penuh sewarna background login card
        super().__init__(master, fg_color="#111827", corner_radius=0, **kwargs)
        
        self.session_user = session_user
        self.on_completion_success = on_completion_success
        self.user_repo = UserRepository()
        
        self._setup_ui()

    def _setup_ui(self):
        # Central Form Card
        self.card = ctk.CTkFrame(self, fg_color="#1F2937", corner_radius=12, width=420, height=420)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Header Icon & Title
        self.icon_label = ctk.CTkLabel(self.card, text="👋🌟", font=ctk.CTkFont(size=36))
        self.icon_label.pack(pady=(35, 5))

        self.title_label = ctk.CTkLabel(
            self.card, 
            text="Lengkapi Profil Anda", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=5)

        self.subtitle_label = ctk.CTkLabel(
            self.card, 
            text="Ini adalah login pertama Anda. Mohon lengkapi\ndata identitas Anda sebelum masuk ke workspace.", 
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF",
            justify="center"
        )
        self.subtitle_label.pack(pady=(0, 25))

        # Terkunci: Email Info
        self.email_label = ctk.CTkLabel(self.card, text="Email Terdaftar", font=ctk.CTkFont(size=12), text_color="#9CA3AF")
        self.email_label.pack(anchor="w", padx=40, pady=(5, 2))
        
        self.entry_email = ctk.CTkEntry(
            self.card, width=340, height=35, fg_color="#2D3748", border_color="#4B5563", text_color="#A0AEC0"
        )
        self.entry_email.insert(0, self.session_user.get("email", ""))
        self.entry_email.configure(state="disabled")  # Email tidak boleh diubah staf
        self.entry_email.pack(padx=40)

        # Input: Nama Lengkap
        self.name_label = ctk.CTkLabel(self.card, text="Nama Lengkap Karyawan", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.name_label.pack(anchor="w", padx=40, pady=(15, 2))
        
        self.entry_name = ctk.CTkEntry(
            self.card, 
            width=340, 
            height=35, 
            placeholder_text="Masukkan nama lengkap sesuai KTP...",
            fg_color="#374151", 
            border_color="#4B5563",
            text_color="#FFFFFF"
        )
        self.entry_name.pack(padx=40)
        self.entry_name.focus_set()

        # Button Submit
        self.btn_submit = ctk.CTkButton(
            self.card, 
            text="Simpan Profil & Masuk Workspace", 
            command=self._handle_submit_click,
            width=340,
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981", 
            hover_color="#059669"
        )
        self.btn_submit.pack(pady=(35, 10))

    def _handle_submit_click(self):
        nama = self.entry_name.get().strip()

        if not nama:
            # Menggunakan Toast.error daripada messagebox jadul
            Toast.error(master=self.winfo_toplevel(), message="Nama Lengkap tidak boleh kosong!")
            return

        if len(nama) < 3:
            Toast.error(master=self.winfo_toplevel(), message="Nama terlalu pendek (Minimal 3 karakter)!")
            return

        self.btn_submit.configure(state="disabled", text="Menyimpan Data...")
        
        # Jalankan background worker thread
        threading.Thread(target=self._update_profile_worker, args=(nama,), daemon=True).start()

    def _update_profile_worker(self, nama: str):
        idUser = self.session_user.get("idUser")
        
        update_payload = {
            "nama": nama,
            "isProfileComplete": True
        }
        
        success = self.user_repo.update_user_profile(idUser, update_payload)
        
        if success:
            self.session_user["nama"] = nama
            self.session_user["isProfileComplete"] = True
            
            # 🌟 EKSEKUSI TOAST: Menggunakan self.winfo_toplevel() sebagai master window
            self.after(0, lambda: Toast.success(
                master=self.winfo_toplevel(), 
                message="Profil berhasil diperbarui! Membuka workspace..."
            ))
            
            # Alihkan kembali penanganan UI ke thread utama Tkinter
            self.after(200, lambda: self.on_completion_success(self.session_user))
        else:
            self.after(0, lambda: self.btn_submit.configure(state="normal", text="Simpan Profil & Masuk Workspace"))
            self.after(0, lambda: Toast.error(
                master=self.winfo_toplevel(), 
                message="Gagal sinkronisasi data ke Firebase."
            ))