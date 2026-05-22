"""
Component: StatusBar
"""

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """Status bar component."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, **kwargs)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Siap",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.status_label.pack(side="left", padx=15, pady=5)
    
    def set_status(self, message: str, status_type: str = "info"):
        colors = {
            "info": "gray50",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
       