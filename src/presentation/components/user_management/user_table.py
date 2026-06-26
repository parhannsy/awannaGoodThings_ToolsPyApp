"""
Component: UserTable
Menangani rendering visual data karyawan dalam bentuk tabular beserta status manajemen aktif.
Menggunakan pemisahan warna badge dinamis per role (Advertiser, Keuangan, Admin).
"""

import customtkinter as ctk
import tkinter as tk


class UserTable(ctk.CTkFrame):
    def __init__(self, master, on_toggle_status_callback, on_edit_row_callback=None, on_change_password_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_toggle_status = on_toggle_status_callback
        self.on_edit_row = on_edit_row_callback
        self.on_change_password = on_change_password_callback
        self._show_actions = False
        
        # Definisikan objek font di luar loop untuk mencegah bottleneck render thread
        self.font_normal = ctk.CTkFont(size=13)
        self.font_placeholder = ctk.CTkFont(size=13, slant="italic")
        self.font_badge = ctk.CTkFont(size=11, weight="bold")
        self.font_header = ctk.CTkFont(size=12, weight="bold")
        
        # 🌟 MATRIKS WARNA: Identitas warna visual per departemen karyawan
        self.role_color_matrix = {
            "advertiser": "#3B82F6",  # Biru Elegan (Marketing)
            "keuangan": "#10B981",    # Hijau Emerald (Finance)
            "admin": "#EC4899"        # Pink/Magenta Administratif (Super Control)
        }
        
        self._setup_header()
        
        # Scrollable container (canvas) untuk mendukung scroll horizontal + vertical
        self._build_scrollable_area()

    def _build_scrollable_area(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=(5, 0))

        # Canvas (tkinter) untuk kemampuan layout konten fleksibel
        self.canvas = tk.Canvas(container, bg="#0B1220", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Inner frame (CTk) di atas canvas
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind resize events untuk menyesuaikan scrollregion
        def _on_config(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.inner_frame.bind("<Configure>", _on_config)
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.inner_id, width=e.width))

    def _setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="#1F2937", height=40, corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        headers = [("Nama / Panggilan", 0.03), ("Email Karyawan", 0.33), ("Role", 0.63), ("Status karyawan", 0.82)]
        for text, rel_x in headers:
            lbl = ctk.CTkLabel(
                header_frame, text=text, font=self.font_header,
                text_color="#9CA3AF", anchor="w"
            )
            lbl.place(relx=rel_x, rely=0.5, anchor="w")

    def render_rows(self, users: list):
        """Merender ulang baris data karyawan di dalam scroll container."""
        # Bersihkan baris lama dari memori secara total
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
            
        if not users:
            no_data = ctk.CTkLabel(self.inner_frame, text="Tidak ada data karyawan ditemukan.", text_color="#6B7280")
            no_data.pack(pady=40)
            return

        for index, user in enumerate(users):
            row = ctk.CTkFrame(
                self.inner_frame, 
                fg_color="#111827" if index % 2 == 0 else "#1F2937", 
                height=50, 
                corner_radius=6
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # 1. Parsing Nilai Nama dengan Format "nama (panggilan)"
            nama = str(user.get('nama', '')).strip()
            panggilan = str(user.get('panggilan', '')).strip()

            # Pengondisian Evaluasi Teks Placeholder Nama
            if not nama and not panggilan:
                nama_text = "Pengguna belum menambahkan nama"
                text_color_name = "#9CA3AF"
                current_font = self.font_placeholder
            else:
                nama_display = nama if nama else "-"
                panggilan_display = panggilan if panggilan else "-"
                nama_text = f"{nama_display} ({panggilan_display})"
                text_color_name = "#FFFFFF"
                current_font = self.font_normal

            lbl_name = ctk.CTkLabel(row, text=nama_text, text_color=text_color_name, font=current_font)
            lbl_name.place(relx=0.03, rely=0.5, anchor="w")

            # 2. Email
            lbl_email = ctk.CTkLabel(row, text=user.get("email", "-"), text_color="#9CA3AF", font=self.font_normal)
            lbl_email.place(relx=0.33, rely=0.5, anchor="w")

            # 3. Role Access Badge dengan Pewarnaan Dinamis
            role = str(user.get("role", "advertiser")).strip().lower()
            text_color_badge = self.role_color_matrix.get(role, "#9CA3AF")
            
            lbl_role = ctk.CTkLabel(
                row, text=role.upper(),
                text_color=text_color_badge,
                font=self.font_badge
            )
            lbl_role.place(relx=0.63, rely=0.5, anchor="w")

            # 4. Soft Delete Toggle Switch Status
            is_active = user.get("isActive", True)
            switch_status = ctk.CTkSwitch(
                row, text="Aktif" if is_active else "Nonaktif",
                text_color="#10B981" if is_active else "#EF4444",
                progress_color="#10B981",
                command=lambda u=user: self.on_toggle_status(u)
            )
            if is_active:
                switch_status.select()
            switch_status.place(relx=0.82, rely=0.5, anchor="w")

            # 5. Action Column (tampil hanya saat edit mode aktif)
            if self._show_actions:
                action_frame = ctk.CTkFrame(row, fg_color="transparent")
                action_frame.place(relx=0.94, rely=0.5, anchor="w")

                # Tombol Edit per baris
                btn_edit = ctk.CTkButton(
                    action_frame, text="Edit", width=80,
                    fg_color="#3B82F6", hover_color="#2563EB",
                    command=(lambda u=user: self.on_edit_row(u)) if self.on_edit_row else (lambda: None)
                )
                btn_edit.pack(side="left", padx=(0, 6))

                # Tombol ganti password (hanya untuk akun role mentor atau admin dan yang memiliki email)
                role_allowed = str(user.get('role', '')).strip().lower() in ("mentor", "admin")
                if user.get("email") and role_allowed:
                    lbl_change_pw = ctk.CTkLabel(
                        action_frame, text="ganti password", text_color="#9CA3AF", cursor="hand2"
                    )
                    # Pasang event click untuk label ganti password
                    lbl_change_pw.bind("<Button-1>", lambda e, u=user: self.on_change_password(u) if self.on_change_password else None)
                    lbl_change_pw.pack(side="left")

    def set_show_actions(self, enabled: bool):
        self._show_actions = enabled
        # Re-render is caller responsibility in index view; optionally could refresh current rows