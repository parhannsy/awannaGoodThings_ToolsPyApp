"""
Komponen: InfoSection (Generik)
Menampilkan info rangkuman teks dinamis dan warning berdasarkan kebutuhan halaman.
"""

import customtkinter as ctk


class InfoSection:
    """Section generik untuk info dan warning labels."""

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._setup_ui()

    def _setup_ui(self):
        """Setup info dan warning labels."""
        self.info_label = ctk.CTkLabel(
            self.parent,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.info_label.pack(anchor="w", padx=15, pady=(0, 3))

        self.warning_label = ctk.CTkLabel(
            self.parent,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        self.warning_label.pack(anchor="w", padx=15, pady=(0, 3))

    def display_info(self, text_content: str):
        """
        Menampilkan teks informasi kustom apa saja dari luar.
        Sangat fleksibel untuk Regional Summary maupun Rate Zonasi.
        """
        self.info_label.configure(text=text_content)

    def display_warning(self, text_warning: str):
        """Menampilkan teks peringatan kustom dari luar."""
        self.warning_label.configure(text=text_warning)

    def clear(self):
        """Clear both labels."""
        self.info_label.configure(text="")
        self.warning_label.configure(text="")