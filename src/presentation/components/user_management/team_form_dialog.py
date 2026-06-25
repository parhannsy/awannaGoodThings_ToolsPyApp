"""
Component: TeamFormDialog
Modal dialog pop-up untuk operasi Create (Tambah) data tim offline.
"""

import threading
import customtkinter as ctk
from presentation.components.shared.toast import Toast


class TeamFormDialog(ctk.CTkToplevel):
    def __init__(self, master, user_service=None, on_success_callback=None):
        super().__init__(master)

        self.user_service = user_service
        self.on_success = on_success_callback

        self.title("Form Tambah Tim")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color="#1F2937")

        self.transient(master)
        self.attributes("-topmost", True)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.lbl_title = ctk.CTkLabel(
            main_frame,
            text="✨ Tambah Data Tim",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        )
        self.lbl_title.pack(anchor="w", pady=(0, 20))

        self._build_field(main_frame, "Nama Tim / PIC", "nama", "Masukkan nama tim atau PIC...", 320)
        self._build_field(main_frame, "Nama Panggilan", "panggilan", "Masukkan panggilan tim...", 320)
        self._build_field(main_frame, "Alamat", "alamat", "Masukkan alamat tim...", 320)
        self._build_field(main_frame, "No. HP", "nohp", "Masukkan nomor HP kontak tim...", 320)
        self._build_dropdown(main_frame)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(18, 0))

        self.btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Batal",
            width=130,
            height=40,
            fg_color="#4B5563",
            hover_color="#374151",
            command=self.destroy
        )
        self.btn_cancel.pack(side="left")

        self.btn_save = ctk.CTkButton(
            btn_frame,
            text="Simpan Tim",
            width=210,
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._handle_save
        )
        self.btn_save.pack(side="right")

    def _build_field(self, parent, label_text, key, placeholder, width):
        setattr(self, f"lbl_{key}", ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9CA3AF"
        ))
        getattr(self, f"lbl_{key}").pack(anchor="w", pady=(10, 4))

        entry = ctk.CTkEntry(
            parent,
            width=width,
            height=36,
            placeholder_text=placeholder,
            fg_color="#374151",
            border_color="#4B5563",
            text_color="#FFFFFF"
        )
        entry.pack(fill="x")
        setattr(self, f"entry_{key}", entry)

    def _build_dropdown(self, parent):
        self.lbl_role_tim = ctk.CTkLabel(
            parent,
            text="Divisi Lini Tim",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9CA3AF"
        )
        self.lbl_role_tim.pack(anchor="w", pady=(10, 4))

        self.combo_role_tim = ctk.CTkComboBox(
            parent,
            values=["gudang", "customerService", "support"],
            height=36,
            fg_color="#374151",
            border_color="#4B5563",
            button_color="#4B5563",
            text_color="#FFFFFF"
        )
        self.combo_role_tim.pack(fill="x")
        self.combo_role_tim.set("gudang")

    def _handle_save(self):
        nama = self.entry_nama.get().strip()
        panggilan = self.entry_panggilan.get().strip()
        alamat = self.entry_alamat.get().strip()
        nohp = self.entry_nohp.get().strip()
        role_tim = self.combo_role_tim.get().strip()

        if not nama or not panggilan or not alamat or not nohp:
            Toast.error(master=self, message="Semua field wajib diisi sebelum menyimpan.")
            return

        self.btn_save.configure(state="disabled", text="Menyimpan...")
        threading.Thread(target=self._create_team_worker, args=(nama, panggilan, alamat, nohp, role_tim), daemon=True).start()

    def _create_team_worker(self, nama, panggilan, alamat, nohp, role_tim):
        if not self.user_service:
            self.after(0, lambda: Toast.error(master=self, message="User service belum disuntikkan ke TeamFormDialog."))
            return

        payload = {
            "nama": nama,
            "panggilan": panggilan,
            "alamat": alamat,
            "nohp": nohp,
            "role_tim": role_tim,
            "isActive": True,
        }

        success = self.user_service.create_team_profile(payload)
        if success:
            self.after(0, self._finalize_success)
        else:
            self.after(0, lambda: self.btn_save.configure(state="normal", text="Simpan Tim"))
            self.after(0, lambda: Toast.error(master=self, message="Gagal menyimpan data tim."))

    def _finalize_success(self):
        if self.on_success:
            self.on_success()
        self.destroy()
