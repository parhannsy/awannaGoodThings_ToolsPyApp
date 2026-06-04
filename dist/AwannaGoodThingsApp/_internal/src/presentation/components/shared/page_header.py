"""
Komponen Shared: PageHeader
Menampilkan judul dan sub-judul halaman secara konsisten di seluruh aplikasi.
"""

import customtkinter as ctk


class PageHeader(ctk.CTkFrame):
    """Header komponen standar untuk konsistensi judul di setiap View Halaman."""

    def __init__(self, master, title: str, subtitle: str = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title_text = title
        self.subtitle_text = subtitle
        
        self._setup_ui()

    def _setup_ui(self):
        """Build UI Layout Header."""
        # Konfigurasi frame dasar transparan agar menyatu dengan background view
        self.configure(fg_color="transparent")
        
        # Tempelkan header di bagian paling atas frame penampung
        self.pack(fill="x", side="top", pady=(0, 15), padx=5)

        # 1. JUDUL UTAMA (Bold & Ukuran Besar)
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(fill="x", side="top", anchor="w")

        # 2. SUB-JUDUL / DESKRIPSI (Muncul hanya jika diisi)
        if self.subtitle_text:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle_text,
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60"),
                anchor="w"
            )
            self.subtitle_label.pack(fill="x", side="top", anchor="w", pady=(2, 0))