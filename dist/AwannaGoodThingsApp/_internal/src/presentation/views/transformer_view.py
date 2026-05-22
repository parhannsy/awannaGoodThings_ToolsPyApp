"""
View: TransformerView
"""

import customtkinter as ctk


class TransformerView(ctk.CTkFrame):
    """Data transformer view."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Data Transformer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))
        
        placeholder = ctk.CTkLabel(
            self,
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
        placeholder.pack(pady=50)
    
    def on_show(self):
        pass