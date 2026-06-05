import customtkinter as ctk
from tkinter import filedialog


class FileInput(ctk.CTkFrame):
    def __init__(self, master, file_var, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.file_var = file_var

        self.label = ctk.CTkLabel(
            self,
            text="Pilih File",
            anchor="w",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )
        self.label.pack(fill="x", pady=(0, 8))

        self.row = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.row.pack(fill="x")

        self.entry = ctk.CTkEntry(
            self.row,
            textvariable=self.file_var,
            height=38,
            placeholder_text="Pilih file yang akan diproses..."
        )
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.button = ctk.CTkButton(
            self.row,
            text="Browse",
            width=120,
            command=self._browse_file
        )
        self.button.pack(side="right")

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.file_var.set(file_path)