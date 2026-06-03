"""
Komponen: TableCard (Generik)
Single table card dinamis untuk menampilkan data berbasis baris dan kolom apa saja.
"""

import customtkinter as ctk


class TableCard(ctk.CTkFrame):
    """Card tabel dinamis yang tidak terikat struktur data tertentu."""

    ACTIVE_BORDER = "#2ecc71"
    INACTIVE_BORDER = ("gray70", "gray30")
    ACTIVE_BG = ("#e8f8f0", "#1a3c2a")

    def __init__(self, master, index, title_str, sub_info_str, headers, rows_data, on_click=None, **kwargs):
        """
        Args:
            master: Parent frame.
            index: Indeks urutan tabel.
            title_str: Judul teks kartu (misal: "Tanggal 2026-05-23").
            sub_info_str: Sub-informasi di bawah judul.
            headers: List string untuk nama kolom, contoh: ["ZONA", "TOTAL", "RTS %"].
            rows_data: List of list/tuple data mentah per baris yang sejajar dengan headers.
            on_click: Callback saat komponen diklik.
        """
        super().__init__(master, **kwargs)
        self.table_index = index
        self.title_str = title_str
        self.sub_info_str = sub_info_str
        self.headers = headers
        self.rows_data = rows_data
        self.on_click = on_click
        self.header_label = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup tabel card secara dinamis."""
        self.configure(
            corner_radius=8,
            border_width=3,
            border_color=self.INACTIVE_BORDER
        )
        self.pack(fill="both", expand=True, pady=2, padx=2)

        # Click binding
        self.bind("<Button-1>", self._on_frame_click)
        self._bind_recursive(self)

        # Header Title
        self.header_label = ctk.CTkLabel(
            self,
            text=self.title_str,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.header_label.pack(anchor="w", padx=10, pady=(6, 1))
        self.header_label.bind("<Button-1>", self._on_frame_click)

        # Sub info
        sub_info = ctk.CTkLabel(
            self,
            text=self.sub_info_str,
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        sub_info.pack(anchor="w", padx=10, pady=(0, 4))
        sub_info.bind("<Button-1>", self._on_frame_click)

        # Table container
        table_container = ctk.CTkFrame(
            self,
            fg_color=("gray90", "gray13"),
            corner_radius=4
        )
        table_container.pack(fill="x", expand=True, padx=10, pady=(0, 8))

        # Header row (Dinamis Berdasarkan Jumlah Headers)
        header_frame = ctk.CTkFrame(table_container, fg_color=("gray80", "gray17"))
        header_frame.pack(fill="x", pady=1)

        for idx, header_text in enumerate(self.headers):
            # Kolom pertama otomatis dibuat lebar/expand (biasanya untuk Nama Daerah/Provinsi/Zona)
            if idx == 0:
                ctk.CTkLabel(
                    header_frame, text=str(header_text).upper(),
                    font=ctk.CTkFont(size=11, weight="bold")
                ).pack(side="left", padx=8, pady=4, expand=True)
            else:
                ctk.CTkLabel(
                    header_frame, text=str(header_text).upper(),
                    font=ctk.CTkFont(size=11, weight="bold"),
                    width=80
                ).pack(side="left", padx=8, pady=4)

        # Data rows (Dinamis Berdasarkan rows_data)
        for r_idx, row in enumerate(self.rows_data):
            row_frame = ctk.CTkFrame(
                table_container,
                fg_color="transparent"
            )
            row_frame.pack(fill="x", pady=1)

            bg = ("gray95", "gray15") if r_idx % 2 == 0 else "transparent"
            row_frame.configure(fg_color=bg)

            for c_idx, cell_value in enumerate(row):
                if c_idx == 0:
                    ctk.CTkLabel(
                        row_frame, text=str(cell_value),
                        font=ctk.CTkFont(size=10)
                    ).pack(side="left", padx=8, pady=2, expand=True)
                else:
                    ctk.CTkLabel(
                        row_frame, text=str(cell_value),
                        font=ctk.CTkFont(size=10),
                        width=80
                    ).pack(side="left", padx=8, pady=2)

    def _bind_recursive(self, widget):
        """Bind click ke semua child widgets."""
        widget.bind("<Button-1>", self._on_frame_click)
        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_frame_click(self, event=None):
        """Handle click pada tabel."""
        if self.on_click:
            self.on_click(self.table_index)

    def set_active(self, active=True):
        """Set visual state aktif/tidak."""
        if active:
            self.configure(
                border_color=self.ACTIVE_BORDER,
                fg_color=self.ACTIVE_BG
            )
        else:
            self.configure(
                border_color=self.INACTIVE_BORDER,
                fg_color=("gray86", "gray17")
            )

    def get_header_label(self):
        """Return header label untuk scroll reference."""
        return self.header_label