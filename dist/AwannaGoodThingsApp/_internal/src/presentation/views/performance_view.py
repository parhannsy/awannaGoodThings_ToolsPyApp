"""
View: PerformanceView
"""

import customtkinter as ctk


class PerformanceView(ctk.CTkFrame):
    """Performance tracker view."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Performance Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))
        
        placeholder = ctk.CTkLabel(
            self,
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
        placeholder.pack(pady=50)
    
    def on_show(self):
        pass