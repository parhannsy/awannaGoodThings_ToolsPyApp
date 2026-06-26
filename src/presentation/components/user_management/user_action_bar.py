"""
Component: UserActionBar
Menangani input pencarian data karyawan, pembersihan query pencarian, 
dan memicu pembukaan form dialog karyawan baru dengan tata letak tombol yang presisi.
"""

import customtkinter as ctk


class UserActionBar(ctk.CTkFrame):
    def __init__(self, master, on_search_callback, on_add_click_callback, on_edit_toggle_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", height=50, **kwargs)
        
        self.on_search = on_search_callback
        self.on_add_click = on_add_click_callback
        self.on_edit_toggle = on_edit_toggle_callback
        self._edit_mode = False
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. CONTAINER AREA PENCARIAN (Merapat di Sisi Kiri)
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

        # TOMBOL SILANG (Clear Search Button)
        self.btn_clear_search = ctk.CTkButton(
            self.search_container, text="×", width=30,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#374151", hover_color="#4B5563", text_color="#9CA3AF",
            command=self._clear_search
        )
        self.btn_clear_search.pack_forget()

        # 2. 🌟 TOMBOL EDIT MODE (Dipasang paling kanan terlebih dahulu)
        self.btn_edit_toggle = ctk.CTkButton(
            self, text="Edit", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF",
            command=self._handle_edit_toggle
        )
        # Menempati ujung kanan layar dengan margin kanan 5 piksel agar tidak menempel dinding
        self.btn_edit_toggle.pack(side="right", fill="y", padx=(0, 5))

        # 3. 🌟 TOMBOL TAMBAH KARYAWAN (Dipasang setelah tombol edit, otomatis berada di sebelah kirinya)
        self.btn_add_user = ctk.CTkButton(
            self, text="+ Tambah Karyawan", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B82F6", hover_color="#2563EB", text_color="#FFFFFF",
            command=self.on_add_click
        )
        # Menggunakan padx=(0, 10) untuk memberikan jarak pemisah (gap) sebesar 10 piksel tepat di antara kedua tombol
        self.btn_add_user.pack(side="right", fill="y", padx=(0, 10))

    def _handle_key_release(self):
        """Mengelola visibilitas tombol silang berdasarkan isi teks entry."""
        query = self.search_entry.get().strip()
        
        if query:
            self.btn_clear_search.pack(side="left", fill="y", padx=(5, 0))
        else:
            self.btn_clear_search.pack_forget()
            
        self.on_search(query)

    def _clear_search(self):
        """Menghapus query, menyembunyikan tombol silang, dan mengembalikan state data awal."""
        self.search_entry.delete(0, "end")
        self.focus_set()
        self.btn_clear_search.pack_forget()
        self.on_search("")

    def _handle_edit_toggle(self):
        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            self.btn_edit_toggle.configure(fg_color="#F59E0B", text="Selesai")
        else:
            self.btn_edit_toggle.configure(fg_color="#10B981", text="Edit")

        if self.on_edit_toggle:
            self.on_edit_toggle(self._edit_mode)