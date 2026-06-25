"""
View: CompleteProfileView
Halaman interupsi berlayar penuh yang memaksa pengguna baru untuk melengkapi 
data profil mereka dalam tiga langkah bertahap sebelum masuk ke dashboard.
"""

import customtkinter as ctk
import threading
from presentation.components.shared.toast import Toast


class CompleteProfileView(ctk.CTkFrame):
    def __init__(self, master, session_user: dict, user_service, on_completion_success: callable, **kwargs):
        super().__init__(master, fg_color="#111827", corner_radius=0, **kwargs)

        self.session_user = session_user
        self.user_service = user_service
        self.on_completion_success = on_completion_success
        self.current_step = self._determine_current_step()

        self._setup_ui()

    def _setup_ui(self):
        self.card = ctk.CTkFrame(self, fg_color="#1F2937", corner_radius=12, width=440, height=560)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        self.icon_label = ctk.CTkLabel(self.card, text="👋🌟", font=ctk.CTkFont(size=36))
        self.icon_label.pack(pady=(25, 5))

        self.title_label = ctk.CTkLabel(
            self.card,
            text="Lengkapi Profil Anda",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=5)

        self.subtitle_label = ctk.CTkLabel(
            self.card,
            text="Akun belum lengkap. Isi data profil bertahap agar dapat masuk ke dashboard.",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF",
            justify="center"
        )
        self.subtitle_label.pack(pady=(0, 15))

        self.email_label = ctk.CTkLabel(self.card, text="Email Terdaftar", font=ctk.CTkFont(size=12), text_color="#9CA3AF")
        self.email_label.pack(anchor="w", padx=40, pady=(5, 2))

        self.entry_email = ctk.CTkEntry(
            self.card, width=360, height=35, fg_color="#2D3748", border_color="#4B5563", text_color="#A0AEC0"
        )
        self.entry_email.insert(0, self.session_user.get("email", ""))
        self.entry_email.configure(state="disabled")
        self.entry_email.pack(padx=40)

        self.form_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=40, pady=(15, 0))

        self.button_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=40, pady=(12, 22))

        self.btn_back = ctk.CTkButton(
            self.button_frame,
            text="←",
            command=self._handle_back_click,
            width=50,
            height=42,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        self.btn_back.pack(side="left")

        self.btn_submit = ctk.CTkButton(
            self.button_frame,
            text="Simpan Profil & Lanjutkan",
            command=self._handle_submit_click,
            width=280,
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669"
        )
        self.btn_submit.pack(side="right")

        self._build_form_fields()

    def _determine_current_step(self) -> int:
        if not str(self.session_user.get("nama", "")).strip() or not str(self.session_user.get("panggilan", "")).strip():
            return 1
        if not str(self.session_user.get("alamat", "")).strip() or not str(self.session_user.get("nohp", "")).strip():
            return 2
        if not str(self.session_user.get("bank", "")).strip() or not str(self.session_user.get("nomor_rekening", "")).strip():
            return 3
        return 1

    def _build_form_fields(self):
        for child in self.form_frame.winfo_children():
            child.destroy()

        if self.current_step == 1:
            self._build_step_one()
        elif self.current_step == 2:
            self._build_step_two()
        else:
            self._build_step_three()

    def _build_step_one(self):
        self.step_label = ctk.CTkLabel(self.form_frame, text="Langkah 1: Nama Lengkap dan Panggilan", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
        self.step_label.pack(anchor="w", pady=(0, 10))

        self.name_label = ctk.CTkLabel(self.form_frame, text="Nama Lengkap", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.name_label.pack(anchor="w", pady=(5, 2))
        self.entry_name = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan nama lengkap sesuai KTP...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_name.insert(0, self.session_user.get("nama", ""))
        self.entry_name.pack(pady=(0, 10))
        self.entry_name.focus_set()

        self.nickname_label = ctk.CTkLabel(self.form_frame, text="Nama Panggilan", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.nickname_label.pack(anchor="w", pady=(5, 2))
        self.entry_nickname = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan nama panggilan...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_nickname.insert(0, self.session_user.get("panggilan", ""))
        self.entry_nickname.pack(pady=(0, 10))

        self.btn_back.pack_forget()
        self.btn_submit.configure(text="Lanjutkan Ke Langkah Berikutnya")

    def _build_step_two(self):
        self.step_label = ctk.CTkLabel(self.form_frame, text="Langkah 2: Alamat dan No. HP", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
        self.step_label.pack(anchor="w", pady=(0, 10))

        self.address_label = ctk.CTkLabel(self.form_frame, text="Alamat", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.address_label.pack(anchor="w", pady=(5, 2))
        self.entry_address = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan alamat lengkap...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_address.insert(0, self.session_user.get("alamat", ""))
        self.entry_address.pack(pady=(0, 10))
        self.entry_address.focus_set()

        self.phone_label = ctk.CTkLabel(self.form_frame, text="No. HP", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.phone_label.pack(anchor="w", pady=(5, 2))
        self.entry_phone = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan nomor HP aktif...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_phone.insert(0, self.session_user.get("nohp", ""))
        self.entry_phone.pack(pady=(0, 10))

        self.btn_back.pack(side="left")
        self.btn_submit.configure(text="Lanjutkan Ke Langkah Berikutnya")

    def _build_step_three(self):
        self.step_label = ctk.CTkLabel(self.form_frame, text="Langkah 3: Bank dan Nomor Rekening", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
        self.step_label.pack(anchor="w", pady=(0, 10))

        self.bank_label = ctk.CTkLabel(self.form_frame, text="Bank", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.bank_label.pack(anchor="w", pady=(5, 2))
        self.entry_bank = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan nama bank...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_bank.insert(0, self.session_user.get("bank", ""))
        self.entry_bank.pack(pady=(0, 10))
        self.entry_bank.focus_set()

        self.account_label = ctk.CTkLabel(self.form_frame, text="Nomor Rekening", font=ctk.CTkFont(size=12), text_color="#E5E7EB")
        self.account_label.pack(anchor="w", pady=(5, 2))
        self.entry_account = ctk.CTkEntry(self.form_frame, width=360, height=35, placeholder_text="Masukkan nomor rekening...", fg_color="#374151", border_color="#4B5563", text_color="#FFFFFF")
        self.entry_account.insert(0, self.session_user.get("nomor_rekening", ""))
        self.entry_account.pack(pady=(0, 10))

        self.btn_back.pack(side="left")
        self.btn_submit.configure(text="Simpan & Masuk Workspace")

    def _handle_submit_click(self):
        if self.current_step == 1:
            nama = self.entry_name.get().strip()
            panggilan = self.entry_nickname.get().strip()

            if not nama:
                Toast.error(master=self.winfo_toplevel(), message="Nama Lengkap tidak boleh kosong!")
                return
            if len(nama) < 3:
                Toast.error(master=self.winfo_toplevel(), message="Nama terlalu pendek (Minimal 3 karakter)!")
                return
            if not panggilan:
                Toast.error(master=self.winfo_toplevel(), message="Nama panggilan tidak boleh kosong!")
                return

            self.btn_submit.configure(state="disabled", text="Menyimpan Data...")
            threading.Thread(target=self._update_profile_worker, args=(
                {"nama": nama, "panggilan": panggilan},
                False
            ), daemon=True).start()
            return

        if self.current_step == 2:
            alamat = self.entry_address.get().strip()
            nohp = self.entry_phone.get().strip()

            if not alamat:
                Toast.error(master=self.winfo_toplevel(), message="Alamat tidak boleh kosong!")
                return
            if not nohp:
                Toast.error(master=self.winfo_toplevel(), message="Nomor HP tidak boleh kosong!")
                return

            self.btn_submit.configure(state="disabled", text="Menyimpan Data...")
            threading.Thread(target=self._update_profile_worker, args=(
                {"alamat": alamat, "nohp": nohp},
                False
            ), daemon=True).start()
            return

        if self.current_step == 3:
            bank = self.entry_bank.get().strip()
            nomor_rekening = self.entry_account.get().strip()

            if not bank:
                Toast.error(master=self.winfo_toplevel(), message="Bank tidak boleh kosong!")
                return
            if not nomor_rekening:
                Toast.error(master=self.winfo_toplevel(), message="Nomor rekening tidak boleh kosong!")
                return

            self.btn_submit.configure(state="disabled", text="Menyimpan Data...")
            threading.Thread(target=self._update_profile_worker, args=(
                {"bank": bank, "nomor_rekening": nomor_rekening, "isProfileComplete": True},
                True
            ), daemon=True).start()
            return

    def _update_profile_worker(self, profile_updates: dict, finalize: bool):
        idUser = self.session_user.get("idUser")
        success = self.user_service.update_user_profile(idUser, profile_updates)

        if success:
            self.session_user.update(profile_updates)
            if finalize:
                self.session_user["isProfileComplete"] = True

            self.after(0, lambda: Toast.success(
                master=self.winfo_toplevel(),
                message="Data profil berhasil diperbarui."
            ))

            if finalize:
                self.after(200, lambda: self.on_completion_success(self.session_user))
            else:
                self.current_step += 1
                self.after(200, self._reset_form_for_next_step)
            return

        self.after(0, lambda: self.btn_submit.configure(state="normal", text="Simpan Profil & Lanjutkan"))
        self.after(0, lambda: Toast.error(
            master=self.winfo_toplevel(),
            message="Gagal sinkronisasi data ke Firebase."
        ))

    def _handle_back_click(self):
        """Kembali ke langkah sebelumnya tanpa menyimpan data."""
        if self.current_step > 1:
            self.current_step -= 1
            self.btn_submit.configure(state="normal", text="Simpan Profil & Lanjutkan")
            self._build_form_fields()

    def _reset_form_for_next_step(self):
        self.btn_submit.configure(state="normal")
        self._build_form_fields()
