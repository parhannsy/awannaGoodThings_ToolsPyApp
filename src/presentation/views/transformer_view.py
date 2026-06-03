"""
View: TransformerView
Halaman transformasi dan cleaning data dengan komponen modular.
"""

import customtkinter as ctk

from src.presentation.components.shared.page_header import PageHeader


class TransformerView(ctk.CTkFrame):
    """View orchestrator untuk Data Transformer."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # Page Title
        self.header = PageHeader(
            master=self,
            title="Data Transformer",
            subtitle="Alat bantu yang diminta sama baginda kanjeng dimas adipati IDUY sang ATMIN😊🙏."
        )

        # Placeholder Content Card
        self.content_card = ctk.CTkFrame(self, fg_color=("gray86", "gray17"), corner_radius=8)
        self.content_card.pack(fill="both", expand=True, pady=(5, 0))

        self.placeholder = ctk.CTkLabel(
            self.content_card,
            text="Fitur ini akan menangani transformasi dan cleaning data.\n\n"
                 "Status: Under Development\n\n"
                 "Fitur yang akan tersedia:\n"
                 "• Mapping kolom dinamis\n"
                 "• Cleaning data kosong/duplikat\n"
                 "• Format konversi (tanggal, currency, dll)\n"
                 "• Preview hasil transformasi",
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=700
        )
        self.placeholder.pack(pady=50)

    def on_show(self):
        pass