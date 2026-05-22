"""
Komponen: InputSection
Area input file, tombol browse, proses, dan bersihkan.
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog


class InputSection(ctk.CTkFrame):
    """Section untuk input file dan action buttons."""

    def __init__(self, master, on_browse=None, on_process=None, on_clear=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_browse = on_browse
        self.on_process = on_process
        self.on_clear = on_clear
        self.current_file_path = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI layout."""
        self.configure(corner_radius=8, height=55)
        self.pack(fill="x", pady=(0, 5), padx=0)
        self.pack_propagate(False)

        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(fill="both", expand=True, padx=8, pady=4)

        # KIRI: File label + Browse
        file_frame = ctk.CTkFrame(input_row, fg_color="transparent")
        file_frame.pack(side="left", fill="both", expand=True)

        self.file_path_label = ctk.CTkLabel(
            file_frame,
            text="Belum ada file dipilih",
            font=ctk.CTkFont(size=9),
            text_color="gray50",
            anchor="w"
        )
        self.file_path_label.pack(anchor="w", pady=(0, 1))

        self.browse_btn = ctk.CTkButton(
            file_frame,
            text="📁 Pilih File",
            command=self._browse_file,
            width=90,
            height=22,
            font=ctk.CTkFont(size=9)
        )
        self.browse_btn.pack(anchor="w")

        # KANAN: Action buttons
        btn_frame = ctk.CTkFrame(input_row, fg_color="transparent")
        btn_frame.pack(side="right", fill="y")

        self.process_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Proses",
            command=self._process_data,
            width=80,
            height=24,
            font=ctk.CTkFont(size=9, weight="bold"),
            state="disabled"
        )
        self.process_btn.pack(side="left", padx=2)

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 Bersihkan",
            command=self._clear_all,
            width=80,
            height=24,
            font=ctk.CTkFont(size=9),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self.clear_btn.pack(side="left", padx=2)

    def _browse_file(self):
        """Browse for file."""
        file_path = filedialog.askopenfilename(
            title="Pilih File Data",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.current_file_path = Path(file_path)
            self.file_path_label.configure(
                text=f"📄 {self.current_file_path.name}",
                text_color=("gray10", "gray90")
            )
            self.process_btn.configure(state="normal")
            if self.on_browse:
                self.on_browse(self.current_file_path)

    def _process_data(self):
        """Trigger process callback."""
        if self.on_process and self.current_file_path:
            self.on_process()

    def _clear_all(self):
        """Trigger clear callback."""
        if self.on_clear:
            self.on_clear()

    def reset(self):
        """Reset ke state awal."""
        self.current_file_path = None
        self.file_path_label.configure(text="Belum ada file dipilih", text_color="gray50")
        self.process_btn.configure(state="disabled")

    def get_file_path(self):
        """Return current file path."""
        return self.current_file_path