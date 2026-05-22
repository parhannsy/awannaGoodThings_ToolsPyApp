"""
View: HistoryView
"""

import customtkinter as ctk


class HistoryView(ctk.CTkFrame):
    """History view."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Result History",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))
        
        placeholder = ctk.CTkLabel(
            self,
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
        placeholder.pack(pady=50)
    
    def on_show(self):
        pass