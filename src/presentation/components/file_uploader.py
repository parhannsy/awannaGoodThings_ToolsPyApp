"""
Component: FileUploader
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional


class FileUploader(ctk.CTkFrame):
    """File upload component."""
    
    def __init__(
        self,
        master,
        on_file_selected: Callable[[Path], None],
        file_types=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_file_selected = on_file_selected
        self.file_types = file_types or [("All files", "*.*")]
        self.selected_file: Optional[Path] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.label = ctk.CTkLabel(
            self,
            text="Pilih File Data",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label.pack(pady=(0, 10))
        
        self.path_var = ctk.StringVar(value="Belum ada file dipilih")
        self.path_label = ctk.CTkLabel(
            self,
            textvariable=self.path_var,
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            wraplength=400
        )
        self.path_label.pack(pady=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            self,
            text="Browse File",
            command=self._browse_file,
            width=150,
            height=35
        )
        self.browse_btn.pack(pady=5)
        
        self.info_label = ctk.CTkLabel(
            self,
            text="Format yang didukung: .xlsx, .xls, .csv",
            font=ctk.CTkFont(size=10),
            text_color="gray40"
        )
        self.info_label.pack(pady=(5, 0))
    
    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File Data",
            filetypes=self.file_types
        )
        
        if file_path:
            self.selected_file = Path(file_path)
            self.path_var.set(str(self.selected_file))
            self.on_file_selected(self.selected_file)
    
    def get_file(self) -> Optional[Path]:
        return self.selected_file
    
    def clear(self):
        self.selected_file = None
        self.path_var.set("Belum ada file dipilih")