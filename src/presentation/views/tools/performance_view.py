"""
View: PerformanceView
Halaman pelacakan performa pengolahan data dengan komponen modular.
"""

import customtkinter as ctk

from src.presentation.components.shared.page_header import PageHeader


class PerformanceView(ctk.CTkFrame):
    """View orchestrator untuk Performance Tracker."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # Page Title
        self.header = PageHeader(
            master=self,
            title="Performance Tracker",
            subtitle="Pelacakan real-time performa pengolahan data, kecepatan proses, dan statistik throughput."
        )

        # Placeholder Content Card
        self.content_card = ctk.CTkFrame(self, fg_color=("gray86", "gray17"), corner_radius=8)
        self.content_card.pack(fill="both", expand=True, pady=(5, 0))

        self.placeholder = ctk.CTkLabel(
            self.content_card,
            text="Fitur ini akan melacak performa pengolahan data.\n\n"
                 "Status: Under Development\n\n"
                 "Fitur yang akan tersedia:\n"
                 "• Real-time processing timer\n"
                 "• Statistik kecepatan proses\n"
                 "• Row count dan throughput\n"
                 "• Error rate tracking",
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=700
        )
        self.placeholder.pack(pady=50)

    def on_show(self):
        pass