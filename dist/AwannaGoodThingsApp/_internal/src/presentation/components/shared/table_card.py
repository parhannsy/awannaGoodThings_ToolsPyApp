"""
Komponen: TableCard
Single table untuk 1 tanggal dengan data provinsi.
"""

import customtkinter as ctk


class TableCard(ctk.CTkFrame):
    """Card tabel untuk 1 tanggal."""

    ACTIVE_BORDER = "#2ecc71"
    INACTIVE_BORDER = ("gray70", "gray30")
    ACTIVE_BG = ("#e8f8f0", "#1a3c2a")

    def __init__(self, master, index, date_str, result, on_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.table_index = index
        self.date_str = date_str
        self.result = result
        self.on_click = on_click
        self.df = result['dataframe']
        self.col_province = result['province_col']
        self.header_label = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup tabel card."""
        self.configure(
            corner_radius=8,
            border_width=3,
            border_color=self.INACTIVE_BORDER
        )
        self.pack(fill="both", expand=True, pady=2, padx=2)

        # Click binding
        self.bind("<Button-1>", self._on_frame_click)
        self._bind_recursive(self)

        # Header
        self.header_label = ctk.CTkLabel(
            self,
            text=f"📅 {self.date_str}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.header_label.pack(anchor="w", padx=10, pady=(6, 1))
        self.header_label.bind("<Button-1>", self._on_frame_click)

        # Sub info
        ratio = (self.result['total_paid'] / self.result['total_leads'] * 100) \
            if self.result['total_leads'] > 0 else 0
        sub_info = ctk.CTkLabel(
            self,
            text=f"Lead: {self.result['total_leads']} | Paid: {self.result['total_paid']} | Ratio: {ratio:.1f}%",
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

        # Header row
        header_frame = ctk.CTkFrame(table_container, fg_color=("gray80", "gray17"), height=28)
        header_frame.pack(fill="x", pady=1)
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="PROVINCE",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=8, pady=2, expand=True)
        
        ctk.CTkLabel(
            header_frame, text="LEADS",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=80
        ).pack(side="left", padx=8, pady=2)
        
        ctk.CTkLabel(
            header_frame, text="PAID",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=80
        ).pack(side="left", padx=8, pady=2)

        # Data rows
        for idx, (_, row) in enumerate(self.df.iterrows()):
            row_frame = ctk.CTkFrame(
                table_container,
                fg_color="transparent",
                height=26
            )
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            bg = ("gray95", "gray15") if idx % 2 == 0 else "transparent"
            row_frame.configure(fg_color=bg)

            ctk.CTkLabel(
                row_frame, text=str(row[self.col_province]),
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=8, pady=1, expand=True)
            
            ctk.CTkLabel(
                row_frame, text=str(row['leads']),
                font=ctk.CTkFont(size=10),
                width=80
            ).pack(side="left", padx=8, pady=1)
            
            ctk.CTkLabel(
                row_frame, text=str(row['paid']),
                font=ctk.CTkFont(size=10),
                width=80
            ).pack(side="left", padx=8, pady=1)

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