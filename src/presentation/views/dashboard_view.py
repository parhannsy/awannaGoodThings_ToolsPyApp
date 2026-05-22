"""
View: DashboardView
"""

import customtkinter as ctk

from presentation.components.file_uploader import FileUploader
from infrastructure.config.app_config import AppConfig


class DashboardView(ctk.CTkFrame):
    """Dashboard main view."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config = AppConfig()
        self._setup_ui()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))
        
        welcome_card = ctk.CTkFrame(self, corner_radius=12)
        welcome_card.pack(fill="x", pady=10)
        
        welcome_text = ctk.CTkLabel(
            welcome_card,
            text=f"Selamat datang di {self.config.APP_NAME}!\n\n"
                 "Aplikasi ini membantu Anda mengolah data penjualan dengan fitur:\n"
                 "• Regional Summary - Agregasi data per wilayah\n"
                 "• Data Transformer - Transformasi dan cleaning data\n" 
                 "• Performance Tracker - Monitoring proses pengolahan\n"
                 "• History - Riwayat proses yang telah dilakukan",
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=700
        )
        welcome_text.pack(padx=20, pady=20)
        
        upload_card = ctk.CTkFrame(self, corner_radius=12)
        upload_card.pack(fill="x", pady=20)
        
        upload_title = ctk.CTkLabel(
            upload_card,
            text="Quick Start",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        upload_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.uploader = FileUploader(
            upload_card,
            on_file_selected=self._on_file_selected,
            file_types=self.config.FILE_TYPES
        )
        self.uploader.pack(padx=20, pady=10)
        
        btn_frame = ctk.CTkFrame(upload_card, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 20))
        
        self.process_btn = ctk.CTkButton(
            btn_frame,
            text="Proses Data",
            command=self._process_data,
            width=150,
            state="disabled"
        )
        self.process_btn.pack(side="left", padx=5)
        
        self.reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset",
            command=self._reset,
            width=100,
            fg_color="transparent",
            border_width=1
        )
        self.reset_btn.pack(side="left", padx=5)
    
    def _on_file_selected(self, file_path):
        self.process_btn.configure(state="normal")
        print(f"File selected: {file_path}")
    
    def _process_data(self):
        file = self.uploader.get_file()
        if file:
            print(f"Processing: {file}")
    
    def _reset(self):
        self.uploader.clear()
        self.process_btn.configure(state="disabled")
    
    def on_show(self):
        pass