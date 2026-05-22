"""
BasePageView
Base class untuk semua halaman aplikasi.
Menyediakan layout konsisten dan template methods.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path

import pandas as pd

from src.presentation.components.shared import (
    InputSection,
    InfoSection,
    NavSection,
    TablesContainer,
    ScrollManager,
    ExcelExporter,
)


class BasePageView(ctk.CTkFrame):
    """
    Base class untuk semua halaman aplikasi.
    
    Aturan tampilan yang harus diikuti semua halaman:
    - Padding global: padx=20, pady=20
    - Title: size 24, weight bold, anchor w
    - Input card: corner_radius=8, height=55
    - Output card: corner_radius=12, hidden initially
    - Output title: size 16, weight bold
    - Info: size 11, gray50
    - Warning: size 11, orange
    - Save button: anchor e, padx=15, pady=(3,8)
    """

    # Override di subclass
    PAGE_TITLE = "Page Title"
    OUTPUT_TITLE = "Hasil Analisis"
    SAVE_BUTTON_TEXT = "💾 Save as Excel"
    
    # Multi-tanggal support — override di subclass kalau perlu
    HAS_DATE_NAVIGATION = False
    HAS_EXCEL_EXPORT = True

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.current_results = {}
        self.dates_list = []
        self.active_table_index = 0
        
        self._setup_ui()

    # ==========================================
    # UI SETUP (Template — jangan override kecuali perlu)
    # ==========================================

    def _setup_ui(self):
        """Template layout untuk semua halaman."""
        self.configure(fg_color="transparent")

        # Main container dengan padding global
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        self._setup_title(self.main_container)

        # Input Section (bisa di-skip oleh subclass)
        self._setup_input(self.main_container)

        # Output Card
        self._setup_output(self.main_container)

    def _setup_title(self, parent):
        """Setup page title."""
        ctk.CTkLabel(
            parent,
            text=self.PAGE_TITLE,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

    def _setup_input(self, parent):
        """
        Setup input section.
        Override kalau halaman tidak perlu input file.
        """
        self.input_section = InputSection(
            parent,
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

    def _setup_output(self, parent):
        """Setup output card template."""
        self.output_card = ctk.CTkFrame(parent, corner_radius=12)
        self.output_card.pack(fill="both", expand=True, pady=3)
        self.output_card.pack_forget()  # Hidden initially

        # Output title
        ctk.CTkLabel(
            self.output_card,
            text=self.OUTPUT_TITLE,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(8, 2))

        # Info & Warning section
        self.info_section = InfoSection(self.output_card)

        # Nav section — hanya untuk multi-tanggal
        if self.HAS_DATE_NAVIGATION:
            self.nav_section = NavSection(
                self.output_card,
                on_navigate=self._scroll_to_table
            )
        else:
            self.nav_section = None

        # Scrollable tables container
        self.tables_scroll = ctk.CTkScrollableFrame(
            self.output_card,
            fg_color="transparent"
        )
        self.tables_scroll.pack(fill="both", expand=True, padx=10, pady=0)

        self.tables_container = TablesContainer(
            self.tables_scroll,
            on_table_click=self._on_table_click
        )

        # Scroll manager
        self.scroll_manager = ScrollManager(self.tables_container)

        # Save button
        if self.HAS_EXCEL_EXPORT:
            self._setup_save_button()

    def _setup_save_button(self):
        """Setup save button."""
        self.exporter = ExcelExporter(self._get_export_data)
        ctk.CTkButton(
            self.output_card,
            text=self.SAVE_BUTTON_TEXT,
            command=self.exporter.save,
            width=140,
            height=30,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="e", padx=15, pady=(3, 8))

    # ==========================================
    # ABSTRACT METHODS (WAJIB OVERRIDE)
    # ==========================================

    def _analyze_data(self, df):
        """
        WAJIB OVERRIDE — Logic analisis data tiap halaman beda.
        
        Args:
            df: pandas DataFrame dari file yang diupload
        
        Raises:
            NotImplementedError: kalau tidak di-override
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _analyze_data()"
        )

    def _display_results(self):
        """
        WAJIB OVERRIDE — Tampilkan hasil ke UI.
        
        Raises:
            NotImplementedError: kalau tidak di-override
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _display_results()"
        )

    # ==========================================
    # OPTIONAL OVERRIDE (Template methods)
    # ==========================================

    def _on_file_selected(self, file_path: Path):
        """Callback saat file dipilih. Override kalau perlu."""
        pass

    def _process_data(self):
        """
        Template flow: read file → analyze → display.
        Override kalau flow beda (misal tidak pakai Excel).
        """
        file_path = self.input_section.get_file_path()
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            self._analyze_data(df)
            self._display_results()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses file:\n{str(e)}")

    def _on_table_click(self, index):
        """Handler klik pada tabel. Override kalau behavior beda."""
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):
        """Scroll ke tabel tertentu. Override kalau tidak pakai scroll."""
        if index < 0 or index >= len(self.dates_list):
            return

        self.active_table_index = index
        self._update_active_state()
        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):
        """Update visual active state."""
        self.tables_container.set_active_table(self.active_table_index)
        
        if self.nav_section:
            self.nav_section.set_active(self.active_table_index)

    def _get_export_data(self):
        """Return data untuk export. Override kalau format beda."""
        return self.dates_list, self.current_results

    def _clear_all(self):
        """Clear semua data. Override kalau ada tambahan."""
        self.output_card.pack_forget()
        
        self.current_results = {}
        self.dates_list = []
        self.active_table_index = 0

        if hasattr(self, 'input_section'):
            self.input_section.reset()
        
        self.info_section.clear()
        
        if self.nav_section:
            self.nav_section.clear()
        
        self.tables_container.clear()
        self.scroll_manager.reset_scroll()
        self.scroll_manager.cancel_pending()

    def on_show(self):
        """Called saat halaman ditampilkan. Override kalau perlu init."""
        pass