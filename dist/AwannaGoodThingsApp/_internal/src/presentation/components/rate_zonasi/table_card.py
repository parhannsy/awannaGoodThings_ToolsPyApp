"""
Komponen: RateZonasiTableCard
Kartu tabel khusus untuk menampilkan performa metrik harian analisis Rate Zonasi (6 Kolom).
"""

import customtkinter as ctk


class RateZonasiTableCard(ctk.CTkFrame):
    """Card tabel khusus untuk menampilkan data analisis rate zonasi harian."""

    ACTIVE_BORDER = "#2ecc71"
    INACTIVE_BORDER = ("gray70", "gray30")
    ACTIVE_BG = ("#e8f8f0", "#1a3c2a")

    def __init__(self, master, index, date_str, result, on_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.table_index = index
        self.date_str = date_str
        self.result = result
        self.on_click = on_click
        
        # Ekstraksi parameter khusus dari data_processor zonasi
        self.title_text = result.get("title", f"📅 Penjemputan: {date_str}")
        self.sub_info_text = result.get("sub_info", "")
        self.headers = result.get("headers", ["PROVINSI", "TOTAL RAW", "DELIVE", "RASIO DELIVE", "RTS", "RASIO RTS/DEL"])
        self.rows = result.get("rows", [])
        
        self.header_label = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup arsitektur tata letak grid khusus 6 kolom."""
        self.configure(
            corner_radius=8,
            border_width=3,
            border_color=self.INACTIVE_BORDER
        )
        self.pack(fill="both", expand=True, pady=4, padx=2)

        # Bind event klik pada frame utama dan seluruh anak komponennya
        self.bind("<Button-1>", self._on_frame_click)
        self._bind_recursive(self)

        # 1. JUDUL UTAMA TABEL (Tanggal Penjemputan)
        self.header_label = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.header_label.pack(fill="x", padx=12, pady=(10, 2))

        # 2. SUB INFO PANEL (Metrik Rangkuman Akumulasi Harian)
        if self.sub_info_text:
            self.sub_info_label = ctk.CTkLabel(
                self,
                text=self.sub_info_text,
                font=ctk.CTkFont(size=11),
                text_color="gray50",
                anchor="w"
            )
            self.sub_info_label.pack(fill="x", padx=12, pady=(0, 6))

        # 3. HEADER TABEL (Baris Judul Kolom)
        header_table_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray20"), height=24, corner_radius=4)
        header_table_frame.pack(fill="x", padx=10, pady=2)
        
        # Kolom 1: Provinsi dibuat fleksibel (expand=True) agar teks panjang tidak terpotong
        ctk.CTkLabel(
            header_table_frame, 
            text=self.headers[0],
            font=ctk.CTkFont(size=10, weight="bold"),
            anchor="w"
        )
        header_table_frame.winfo_children()[-1].pack(side="left", padx=8, expand=True, fill="x")

        # Kolom 2 sampai 6: Ukuran statis (width=75) agar susunan grid sejajar lurus ke bawah
        for h_text in self.headers[1:]:
            ctk.CTkLabel(
                header_table_frame, 
                text=h_text,
                font=ctk.CTkFont(size=9, weight="bold"),
                width=75,
                anchor="center"
            )
            header_table_frame.winfo_children()[-1].pack(side="left", padx=4)

        # 4. ISI BARIS DATA PROVINSI (Rows Loop)
        for row_data in self.rows:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=1)

            # Cell Provinsi (Kiri)
            ctk.CTkLabel(
                row_frame, 
                text=str(row_data[0]),
                font=ctk.CTkFont(size=10),
                anchor="w"
            ).pack(side="left", padx=8, expand=True, fill="x")

            # Cell Angka Metrik (Kanan, berurutan sesuai payload)
            for val in row_data[1:]:
                ctk.CTkLabel(
                    row_frame, 
                    text=str(val),
                    font=ctk.CTkFont(size=10),
                    width=75,
                    anchor="center"
                ).pack(side="left", padx=4)

    def _bind_recursive(self, widget):
        """Metode rekursif untuk mengikat event klik dari widget anak ke objek induk."""
        widget.bind("<Button-1>", self._on_frame_click)
        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_frame_click(self, event=None):
        """Mengirimkan sinyal indeks tabel ke orchestrator view saat diklik."""
        if self.on_click:
            self.on_click(self.table_index)

    def set_active(self, active=True):
        """Mengubah identitas visual komponen saat dalam kondisi aktif disorot."""
        if active:
            self.configure(border_color=self.ACTIVE_BORDER, fg_color=self.ACTIVE_BG)
        else:
            self.configure(border_color=self.INACTIVE_BORDER, fg_color="transparent")

    def get_header_label(self):
        """Mengembalikan referensi widget header teks untuk penghitungan jarak scroll otomatis."""
        return self.header_label