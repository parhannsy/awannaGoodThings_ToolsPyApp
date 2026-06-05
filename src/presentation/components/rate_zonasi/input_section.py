"""
Section input file dengan label, entry, tombol browse, process, dan clear.
Desain mengikuti komponen FileInput dengan penambahan tombol aksi.
"""

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from .constant import COLORS, FONTS


class RateZonasiInputSection(ctk.CTkFrame):
    """Section input file dengan label, entry, tombol browse, process, dan clear."""

    def __init__(self, master, on_browse=None, on_process=None, on_clear=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_browse = on_browse
        self.on_process = on_process
        self.on_clear = on_clear
        self.file_path = None

        self._build()

    def _build(self):
        # Label judul section
        self.label = ctk.CTkLabel(
            self,
            text="Pilih File",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label.pack(fill="x", pady=(0, 8))

        # Row container untuk entry + tombol
        self.row = ctk.CTkFrame(self, fg_color="transparent")
        self.row.pack(fill="x")

        # Entry untuk menampilkan path file
        self.entry = ctk.CTkEntry(
            self.row,
            height=38,
            placeholder_text="Pilih file yang akan diproses...",
            state="readonly"
        )
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        # Tombol Browse
        self.btn_browse = ctk.CTkButton(
            self.row,
            text="Browse",
            width=120,
            command=self._browse
        )
        self.btn_browse.pack(side="left", padx=(0, 6))

        # Tombol Proses Data
        self.btn_process = ctk.CTkButton(
            self.row,
            text="▶ Proses Data",
            width=120,
            command=self._process,
            state="disabled",
            fg_color=COLORS["success"],
            font=FONTS["body"]
        )
        self.btn_process.pack(side="left", padx=(0, 6))

        # Tombol Bersihkan
        self.btn_clear = ctk.CTkButton(
            self.row,
            text="🧹 Bersihkan",
            width=120,
            command=self._clear,
            fg_color=COLORS["danger"],
            hover_color="#DC2626",
            font=FONTS["body"]
        )
        self.btn_clear.pack(side="left")

    def _browse(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File Data Pengiriman",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.file_path = Path(file_path)
            display_name = str(self.file_path)

            # Update entry dengan path file
            self.entry.configure(state="normal")
            self.entry.delete(0, "end")
            self.entry.insert(0, display_name)
            self.entry.configure(state="readonly")

            # Enable tombol process
            self.btn_process.configure(state="normal")

            if self.on_browse:
                self.on_browse(self.file_path)

    def _process(self):
        if self.on_process:
            self.on_process()

    def _clear(self):
        self.file_path = None

        # Kosongkan entry
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.configure(state="readonly")

        # Disable tombol process
        self.btn_process.configure(state="disabled")

        if self.on_clear:
            self.on_clear()

    def reset(self):
        self._clear()