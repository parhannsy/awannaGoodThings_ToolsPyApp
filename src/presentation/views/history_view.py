"""
View: HistoryView
Halaman riwayat proses pengolahan data dengan komponen modular.
"""

import customtkinter as ctk

from src.presentation.components.shared.page_header import PageHeader


class HistoryView(ctk.CTkFrame):
    """View orchestrator untuk Result History."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # Page Title
        self.header = PageHeader(
            master=self,
            title="Result History",
            subtitle="Riwayat lengkap proses pengolahan data, detail file, waktu proses, dan status."
        )

        # Placeholder Content Card
        self.content_card = ctk.CTkFrame(self, fg_color=("gray86", "gray17"), corner_radius=8)
        self.content_card.pack(fill="both", expand=True, pady=(5, 0))

        self.placeholder = ctk.CTkLabel(
            self.content_card,
            text="Fitur ini akan menampilkan riwayat proses pengolahan data.\n\n"
                 "Status: Under Development\n\n"
                 "Fitur yang akan tersedia:\n"
                 "• Daftar proses yang telah dilakukan\n"
                 "• Detail file input dan output\n"
                 "• Waktu proses dan status\n"
                 "• Quick re-process dari history",
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=700
        )
        self.placeholder.pack(pady=50)

    def on_show(self):
        pass