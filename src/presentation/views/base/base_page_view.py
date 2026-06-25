"""
BasePageView
Base class untuk semua halaman aplikasi awannaTools.
Menyediakan layout konsisten, template methods, dan fleksibilitas arsitektur.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import pandas as pd

# Kita hanya mengimport komponen dasar yang pasti dipakai semua halaman
from presentation.components.shared import InputSection, InfoSection

class BasePageView(ctk.CTkFrame):
    PAGE_TITLE = "Page Title"
    OUTPUT_TITLE = "Hasil Analisis"
    SAVE_BUTTON_TEXT = "💾 Save as Excel"
    
    HAS_DATE_NAVIGATION = False
    REQUIRES_EXCEL_INPUT = True
    HAS_EXCEL_EXPORT = True

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_results = {}
        self.dates_list = []
        self.active_table_index = 0
        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._setup_title(self.main_container)

        if self.REQUIRES_EXCEL_INPUT:
            self._setup_input(self.main_container)
        else:
            self._setup_custom_input(self.main_container)

        self._setup_output(self.main_container)

    def _setup_title(self, parent):
        ctk.CTkLabel(
            parent,
            text=self.PAGE_TITLE,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

    def _setup_input(self, parent):
        self.input_section = InputSection(
            parent,
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

    def _setup_custom_input(self, parent):
        pass

    def _setup_output(self, parent):
        self.output_card = ctk.CTkFrame(parent, corner_radius=12)
        self.output_card.pack(fill="both", expand=True, pady=3)
        
        if self.REQUIRES_EXCEL_INPUT:
            self.output_card.pack_forget()

        ctk.CTkLabel(
            self.output_card,
            text=self.OUTPUT_TITLE,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(8, 2))

        if not self.REQUIRES_EXCEL_INPUT:
            self._setup_custom_output(self.output_card)
            return

        # 🌟 LAZY IMPORT: Komponen Excel hanya di-import secara dinamis saat halaman berbasis Excel dibuka.
        # Ini mencegah kegagalan program akibat error 'TablesContainer' di shared components.
        from presentation.components.shared import NavSection, TablesContainer, ScrollManager

        self.info_section = InfoSection(self.output_card)

        if self.HAS_DATE_NAVIGATION:
            self.nav_section = NavSection(self.output_card, on_navigate=self._scroll_to_table)
        else:
            self.nav_section = None

        self.tables_scroll = ctk.CTkScrollableFrame(self.output_card, fg_color="transparent")
        self.tables_scroll.pack(fill="both", expand=True, padx=10, pady=0)

        self.tables_container = TablesContainer(self.tables_scroll, on_table_click=self._on_table_click)
        self.scroll_manager = ScrollManager(self.tables_container)

        if self.HAS_EXCEL_EXPORT:
            self._setup_save_button()

    def _setup_custom_output(self, parent):
        pass

    def _setup_save_button(self):
        # 🌟 LAZY IMPORT untuk Exporter Excel
        from presentation.components.shared import ExcelExporter
        self.exporter = ExcelExporter(self._get_export_data)
        ctk.CTkButton(
            self.output_card,
            text=self.SAVE_BUTTON_TEXT,
            command=self.exporter.save,
            width=140,
            height=30,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="e", padx=15, pady=(3, 8))

    def _analyze_data(self, df):
        if self.REQUIRES_EXCEL_INPUT:
            raise NotImplementedError(f"{self.__class__.__name__} must implement _analyze_data()")

    def _display_results(self):
        if self.REQUIRES_EXCEL_INPUT:
            raise NotImplementedError(f"{self.__class__.__name__} must implement _display_results()")

    def _on_file_selected(self, file_path: Path):
        pass

    def _process_data(self):
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
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):
        if index < 0 or index >= len(self.dates_list):
            return
        self.active_table_index = index
        self._update_active_state()
        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):
        if hasattr(self, 'tables_container'):
            self.tables_container.set_active_table(self.active_table_index)
        if hasattr(self, 'nav_section') and self.nav_section:
            self.nav_section.set_active(self.active_table_index)

    def _get_export_data(self):
        return self.dates_list, self.current_results

    def _clear_all(self):
        self.output_card.pack_forget()
        self.current_results = {}
        self.dates_list = []
        self.active_table_index = 0
        if hasattr(self, 'input_section'): self.input_section.reset()
        if hasattr(self, 'info_section'): self.info_section.clear()
        if hasattr(self, 'nav_section') and self.nav_section: self.nav_section.clear()
        if hasattr(self, 'tables_container'): self.tables_container.clear()
        if hasattr(self, 'scroll_manager'):
            self.scroll_manager.reset_scroll()
            self.scroll_manager.cancel_pending()

    def on_show(self):
        pass
