"""
Component: UserActionBar
Menangani input pencarian data karyawan, pembersihan query pencarian, 
dan memicu pembukaan form dialog karyawan baru.
"""

import customtkinter as ctk


class UserActionBar(ctk.CTkFrame):
    def __init__(self, master, on_search_callback, on_add_click_callback, **kwargs):
        super().__init__(master, fg_color="transparent", height=50, **kwargs)
        
        self.on_search = on_search_callback
        self.on_add_click = on_add_click_callback
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. CONTAINER AREA PENCARIAN (Agar Entry dan Tombol Silang Menyatu Rapi)
        self.search_container = ctk.CTkFrame(self, fg_color="transparent")
        self.search_container.pack(side="left", fill="y")

        # Search Entry Bar
        self.search_entry = ctk.CTkEntry(
            self.search_container, width=280, placeholder_text="Cari nama atau email staff...",
            fg_color="#1F2937", border_color="#374151", text_color="#FFFFFF"
        )
        self.search_entry.pack(side="left", fill="y")
        
        # Debounce/Mendengarkan ketikan keyboard
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_key_release())

        # 🌟 TOMBOL SILANG (Clear Search Button)
        # Menggunakan karakter '×' yang tebal dan minimalis
        self.btn_clear_search = ctk.CTkButton(
            self.search_container, text="×", width=30,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#374151", hover_color="#4B5563", text_color="#9CA3AF",
            command=self._clear_search
        )
        # Sembunyikan di awal, tombol hanya muncul jika ada teks di dalam kolom pencarian
        self.btn_clear_search.pack_forget()

        # 2. TOMBOL TAMBAH KARYAWAN
        self.btn_add_user = ctk.CTkButton(
            self, text="+ Tambah Karyawan", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B82F6", hover_color="#2563EB", text_color="#FFFFFF",
            command=self.on_add_click
        )
        self.btn_add_user.pack(side="right", fill="y")

    def _handle_key_release(self):
        """Mengelola visibilitas tombol silang berdasarkan isi teks entry."""
        query = self.search_entry.get().strip()
        
        if query:
            # Jika ada teks, tampilkan tombol silang di sebelah kanan Entry
            self.btn_clear_search.pack(side="left", fill="y", padx=(5, 0))
        else:
            # Jika kosong, sembunyikan tombol silang
            self.btn_clear_search.pack_forget()
            
        # Jalankan fungsi pencarian ke repository
        self.on_search(query)

    def _clear_search(self):
        """Menghapus query, menyembunyikan tombol silang, dan mengembalikan state data awal."""
        # 1. Kosongkan teks di dalam widget Entry
        self.search_entry.delete(0, "end")
        
        # 2. Hilangkan fokus dari Entry agar tidak 'mendengarkan' event secara aktif
        self.focus_set()
        
        # 3. Sembunyikan kembali tombol silang dari layar
        self.btn_clear_search.pack_forget()
        
        # 4. Picu fungsi callback dengan string kosong untuk merender ulang semua data karyawan
        self.on_search("")