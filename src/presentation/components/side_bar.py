"""
Component: Sidebar
Menyediakan panel navigasi utama dengan dukungan Scrollable Viewport, Live Search Filter,
tombol "Clear Search", manajemen visibilitas scrollbar otomatis, fitur Group Menu Expandable,
Indentasi Sub-navigasi, State Label Aktif, dan Pop-up Konfirmasi Logout Modern.
"""

import customtkinter as ctk
from typing import Callable, Dict


class Sidebar(ctk.CTkFrame):
    """Navigation sidebar component with enhanced visual hierarchy and smart states."""

    MENU_GROUPS = [
        {
            "label": "Dashboard",
            "items": [
                {"id": "dashboard", "label": "Dashboard", "icon": "🏠"},
                {"id": "history", "label": "History", "icon": "🕘"},
                {"id": "firebase_status", "label": "Firebase Status", "icon": "⚡"},
            ]
        },
        {
            "label": "Data",
            "items": [
                {"id": "produk_index", "label": "Produk", "icon": "📦"}
            ]
        },
        {
            "label": "Keuangan",
            "items": [
                {"id": "keuangan_index", "label": "Keuangan", "icon": "💰"}
            ]
        },
        {
            "label": "TOOLS",
            "items": [
                {"id": "regional_summary", "label": "Regional Summary", "icon": "📊"},
                {"id": "rate_zonasi", "label": "Rate Zonasi", "icon": "📍"},
                {"id": "transformer", "label": "Data Transformer", "icon": "🔄"},
                {"id": "performance", "label": "Performance", "icon": "📈"},
            ]
        }
    ]

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        on_logout: Callable[[], None],
        app_name: str,
        **kwargs
    ):
        super().__init__(master, width=250, **kwargs)

        self.on_navigate = on_navigate
        self.on_logout = on_logout
        
        # Penampung widget dan status
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.group_labels: Dict[str, ctk.CTkLabel] = {}
        self.item_to_group: Dict[str, str] = {}
        
        # Menyimpan ID halaman yang saat ini sedang aktif
        self.current_active_view: str = ""
        
        # STATE MANAGEMENT UNTUK EXPANDABLE MENU
        self.group_states: Dict[str, bool] = {
            "Dashboard": True,
            "Data": True,
            "Keuangan": True,
            "TOOLS": False
        }

        self._setup_layout()
        self._setup_header(app_name)
        self._setup_search_bar()
        self._setup_menu()
        self._setup_footer()

    def _setup_layout(self):
        self.grid_rowconfigure(1, weight=1)

    def _setup_header(self, app_name: str):
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.pack(fill="x", padx=16, pady=(20, 10))

        logo_label = ctk.CTkLabel(header_container, text="🧩", font=ctk.CTkFont(size=32))
        logo_label.pack(anchor="w")

        app_label = ctk.CTkLabel(
            header_container,
            text=app_name,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        app_label.pack(anchor="w", pady=(4, 0))

        subtitle = ctk.CTkLabel(
            header_container,
            text="Sales Data Workspace",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        subtitle.pack(anchor="w")

        line = ctk.CTkFrame(self, height=2, fg_color=("gray75", "gray25"))
        line.pack(fill="x", padx=15, pady=(10, 10))

    def _setup_search_bar(self):
        """Membuat kolom pencarian dengan tombol silang (Clear) yang dinamis."""
        self.search_container = ctk.CTkFrame(self, fg_color="transparent")
        self.search_container.pack(fill="x", padx=15, pady=(0, 10))
        
        self.search_container.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text="🔍  Search navigation...",
            height=35,
            corner_radius=8,
            fg_color=("gray85", "#2A2A2A"),
            border_color=("gray70", "#3E3E3E"),
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._filter_menu)

        self.btn_clear_search = ctk.CTkButton(
            self.search_container,
            text="✕",
            width=28,
            height=35,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color="gray50",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._clear_search
        )

    def _setup_menu(self):
        self.menu_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40"),
            label_text=""
        )
        self.menu_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        self.empty_state_label = ctk.CTkLabel(
            self.menu_frame,
            text="Ups, halaman tujuanmu\ntidak ada :(",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray50",
            justify="center"
        )
        
        self._render_full_menu()

    def _toggle_group(self, group_name: str):
        """Mengubah status expand/collapse grup menu secara interaktif."""
        self.group_states[group_name] = not self.group_states[group_name]
        self._refresh_menu_display()

    def _refresh_menu_display(self):
        """Mengatur ulang susunan pengepakan widget berdasarkan state expand/collapse saat ini."""
        self.empty_state_label.pack_forget()
        for label in self.group_labels.values():
            label.pack_forget()
        for btn in self.buttons.values():
            btn.pack_forget()

        active_group = self.item_to_group.get(self.current_active_view, "")

        for group in self.MENU_GROUPS:
            group_name = group["label"]
            is_expanded = self.group_states.get(group_name, True)
            
            arrow = "▼" if is_expanded else "▶"
            if group_name in self.group_labels:
                self.group_labels[group_name].configure(text=f"{arrow}  {group_name.upper()}")
                
                if group_name == active_group:
                    self.group_labels[group_name].configure(text_color=("gray10", "gray90"))
                else:
                    self.group_labels[group_name].configure(text_color="gray50")
            
            self.group_labels[group_name].pack(fill="x", padx=14, pady=(14, 6))

            if is_expanded:
                for item in group["items"]:
                    self.buttons[item["id"]].pack(fill="x", pady=3, padx=(28, 6))
                    
        if hasattr(self.menu_frame, "_scrollbar"):
            self.menu_frame._scrollbar.grid_forget()

    def _render_full_menu(self):
        """Membangun total layout widget menu pertama kali secara sekuensial."""
        self.empty_state_label.pack_forget()

        for group in self.MENU_GROUPS:
            group_name = group["label"]
            
            if group_name not in self.group_labels:
                group_label = ctk.CTkLabel(
                    self.menu_frame,
                    text="",
                    anchor="w",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="gray50",
                    cursor="hand2"
                )
                group_label.bind("<Button-1>", lambda event, g=group_name: self._toggle_group(g))
                self.group_labels[group_name] = group_label

            for item in group["items"]:
                if item["id"] not in self.buttons:
                    self.item_to_group[item["id"]] = group_name
                    btn = ctk.CTkButton(
                        self.menu_frame,
                        text=f"{item['icon']}   {item['label']}",
                        anchor="w",
                        height=42,
                        corner_radius=10,
                        border_width=0,
                        fg_color="transparent",
                        hover_color=("gray80", "gray22"),
                        text_color=("gray15", "gray90"),
                        font=ctk.CTkFont(size=13),
                        command=lambda x=item["id"]: self.on_navigate(x)
                    )
                    self.buttons[item["id"]] = btn
                    
        self._refresh_menu_display()

    def _filter_menu(self, event=None):
        """Menyaring tampilan menu secara real-time dan mengelola visibilitas scrollbar secara cerdas."""
        query = self.search_entry.get().strip().lower()
        
        if not query:
            self._clear_search()
            return

        self.btn_clear_search.grid(row=0, column=1, padx=(5, 0), sticky="e")

        self.empty_state_label.pack_forget()
        for label in self.group_labels.values():
            label.pack_forget()
        for btn in self.buttons.values():
            btn.pack_forget()

        any_match_found = False
        total_visible_rows = 0

        for group in self.MENU_GROUPS:
            group_name = group["label"]
            items_matching = [item for item in group["items"] if query in item["label"].lower()]
            
            if items_matching:
                any_match_found = True
                
                self.group_labels[group_name].configure(text=f"▼  {group_name.upper()}")
                self.group_labels[group_name].pack(fill="x", padx=14, pady=(14, 6))
                total_visible_rows += 1
                
                for item in items_matching:
                    self.buttons[item["id"]].pack(fill="x", pady=3, padx=(28, 6))
                    total_visible_rows += 1

        if not any_match_found:
            if hasattr(self.menu_frame, "_scrollbar"):
                self.menu_frame._scrollbar.grid_forget()
            self.empty_state_label.pack(fill="x", pady=40)
            
        elif total_visible_rows <= 5:
            if hasattr(self.menu_frame, "_scrollbar"):
                self.menu_frame._scrollbar.grid_forget()
                
        else:
            if hasattr(self.menu_frame, "_create_grid"):
                self.menu_frame._create_grid()

    def _clear_search(self):
        """Menghapus isi kolom pencarian, menyembunyikan tombol silang, dan mereset urutan menu."""
        self.search_entry.delete(0, 'end')
        self.btn_clear_search.grid_forget()
        self.empty_state_label.pack_forget()
        
        for label in self.group_labels.values():
            label.pack_forget()
        for btn in self.buttons.values():
            btn.pack_forget()
            
        self._refresh_menu_display()
        self.focus_set()

    def _trigger_logout_confirmation(self):
        """🌟 KUSTOM MODAL DIALOG DI TKINTER: Memunculkan konfirmasi logout modern."""
        # Ambil referensi window utama/root
        root = self.winfo_toplevel()
        
        # Buat jendela pop-up kustom berbasis CTkToplevel
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Sign Out")
        dialog.geometry("340x180")
        dialog.resizable(False, False)
        
        # Konfigurasi agar pop-up selalu berada di tengah window utama
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_w = root.winfo_width()
        root_h = root.winfo_height()
        
        pos_x = root_x + (root_w // 2) - (340 // 2)
        pos_y = root_y + (root_h // 2) - (180 // 2)
        dialog.geometry(f"340x180+{pos_x}+{pos_y}")
        
        # SIFAT MODAL PROFESIONAL: Kunci fokus aplikasi hanya pada jendela dialog ini
        dialog.transient(root)
        dialog.grab_set()
        
        # Kustomisasi Konten Dialog
        msg_icon = ctk.CTkLabel(dialog, text="🚪", font=ctk.CTkFont(size=28))
        msg_icon.pack(pady=(20, 5))
        
        msg_label = ctk.CTkLabel(
            dialog, 
            text="Apakah Anda yakin ingin keluar dari akun?",
            font=ctk.CTkFont(size=13, weight="normal"),
            wraplength=300
        )
        msg_label.pack(pady=10, padx=20)
        
        # Container Tombol Aksi
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(fill="x", side="bottom", pady=20, padx=20)
        
        def on_confirm():
            dialog.destroy()
            self.on_logout()  # Jalankan callback logout asli jika menekan keluar
            
        def on_cancel():
            dialog.destroy()  # Tutup modal tanpa aksi jika menekan batal
            
        # Tombol Batal (Gaya Netral)
        btn_cancel = ctk.CTkButton(
            btn_container,
            text="Batal",
            width=140,
            height=34,
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("gray10", "gray90"),
            command=on_cancel
        )
        btn_cancel.pack(side="left", padx=(0, 10))
        
        # Tombol Keluar (Gaya Destruktif / Merah)
        btn_signout = ctk.CTkButton(
            btn_container,
            text="Keluar Akun",
            width=140,
            height=34,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="white",
            command=on_confirm
        )
        btn_signout.pack(side="right")

    def _setup_footer(self):
        footer_container = ctk.CTkFrame(self, fg_color="transparent")
        footer_container.pack(side="bottom", fill="x", padx=15, pady=15)

        line = ctk.CTkFrame(footer_container, height=1, fg_color=("gray75", "gray25"))
        line.pack(fill="x", pady=(0, 10))

        # 🌟 PERBAIKAN: Mengalihkan 'command' langsung ke fungsi pemicu konfirmasi internal kita
        self.btn_logout = ctk.CTkButton(
            footer_container,
            text="🚪   Sign Out",
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#FEE2E2", "#451A03") if ctk.get_appearance_mode() == "Light" else ("gray80", "#3F1A1C"),
            text_color=("#DC2626", "#FCA5A5"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._trigger_logout_confirmation
        )
        self.btn_logout.pack(fill="x", pady=(0, 10))

        footer = ctk.CTkLabel(
            footer_container,
            text="v1.1.0  •  Awanna Media's Data Tool",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        footer.pack()

    def set_active(self, view_id: str):
        """Mengatur tombol navigasi aktif sekaligus memperbarui warna label induknya."""
        self.current_active_view = view_id
        
        for vid, btn in self.buttons.items():
            if vid == view_id:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    hover_color=("gray75", "gray25"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    border_width=1,
                    border_color=("gray65", "gray35")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=("gray80", "gray22"),
                    font=ctk.CTkFont(size=13),
                    border_width=0
                )
        
        self._refresh_menu_display()