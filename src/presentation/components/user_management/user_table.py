"""
Component: UserTable
Menangani rendering visual data karyawan dalam bentuk tabular beserta status manajemen aktif.
Menggunakan pemisahan warna badge dinamis per role (Advertiser, Keuangan, Admin).
"""

import customtkinter as ctk


class UserTable(ctk.CTkFrame):
    def __init__(self, master, on_toggle_status_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_toggle_status = on_toggle_status_callback
        
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
        
        # Scrollable container untuk baris data
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_container.pack(fill="both", expand=True, pady=(5, 0))

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
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
            
        if not users:
            no_data = ctk.CTkLabel(self.scroll_container, text="Tidak ada data karyawan ditemukan.", text_color="#6B7280")
            no_data.pack(pady=40)
            return

        for index, user in enumerate(users):
            row = ctk.CTkFrame(
                self.scroll_container, 
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