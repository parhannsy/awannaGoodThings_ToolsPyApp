import customtkinter as ctk


class ProcessButton(ctk.CTkButton):

    DEFAULT_TEXT = "Proses"
    PROCESSING_TEXT = "Memproses..."

    def __init__(self, master, command=None, **kwargs):
        super().__init__(
            master,
            text=self.DEFAULT_TEXT,
            height=42,
            command=command,
            **kwargs
        )

    def set_processing(self):
        """Ubah tombol ke mode loading."""
        self.configure(
            text=self.PROCESSING_TEXT,
            state="disabled"
        )

    def set_normal(self):
        """Kembalikan tombol ke kondisi normal."""
        self.configure(
            text=self.DEFAULT_TEXT,
            state="normal"
        )