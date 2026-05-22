"""
View: RegionalSummaryView
Halaman agregasi data per wilayah dengan kalibrasi provinsi.
Hanya sebagai orchestrator — memanggil komponen-komponen.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.presentation.components.regional_summary import (
    InputSection,
    InfoSection,
    NavSection,
    TablesContainer,
    ScrollManager,
    ExcelExporter,
)


MASTER_PROVINCES = [
    "BALI", "BANGKA BELITUNG", "BANTEN", "BENGKULU", "DI YOGYAKARTA",
    "DKI JAKARTA", "GORONTALO", "JAMBI", "JAWA BARAT", "JAWA TENGAH",
    "JAWA TIMUR", "KALIMANTAN BARAT", "KALIMANTAN SELATAN", "KALIMANTAN TENGAH",
    "KALIMANTAN TIMUR", "KALIMANTAN UTARA", "KEPULAUAN RIAU", "LAMPUNG",
    "MALUKU", "MALUKU UTARA", "NANGGROE ACEH DARUSSALAM (NAD)",
    "NUSA TENGGARA BARAT (NTB)", "NUSA TENGGARA TIMUR (NTT)", "PAPUA",
    "PAPUA BARAT", "RIAU", "SULAWESI BARAT", "SULAWESI SELATAN",
    "SULAWESI TENGAH", "SULAWESI TENGGARA", "SULAWESI UTARA",
    "SUMATRA BARAT", "SUMATRA SELATAN", "SUMATRA UTARA"
]

ACEH_NAME = "NANGGROE ACEH DARUSSALAM (NAD)"
YOGYA_NAME = "DI YOGYAKARTA"
JAKARTA_NAME = "DKI JAKARTA"

PROVINCE_MAPPING = {
    'ACEH': ACEH_NAME,
    'NAD': ACEH_NAME,
    'NANGGROE ACEH DARUSSALAM (NAD)': ACEH_NAME,

    'YOGYAKARTA': YOGYA_NAME,
    'JOGJA': YOGYA_NAME,
    'DIY': YOGYA_NAME,

    'JAKARTA': JAKARTA_NAME,

    'NTB': 'NUSA TENGGARA BARAT (NTB)',
    'NTT': 'NUSA TENGGARA TIMUR (NTT)',

    'KEP RIAU': 'KEPULAUAN RIAU',
    'KEP. RIAU': 'KEPULAUAN RIAU',

    'BANGKA': 'BANGKA BELITUNG',
    'BABEL': 'BANGKA BELITUNG',

    'SULSEL': 'SULAWESI SELATAN',
    'SULTENG': 'SULAWESI TENGAH',
    'SULTRA': 'SULAWESI TENGGARA',
    'SULUT': 'SULAWESI UTARA',

    'KALBAR': 'KALIMANTAN BARAT',
    'KALSEL': 'KALIMANTAN SELATAN',
    'KALTENG': 'KALIMANTAN TENGAH',
    'KALTIM': 'KALIMANTAN TIMUR',
    'KALUT': 'KALIMANTAN UTARA',
}


MONTH_MAP = {
    'Januari': 1,
    'Februari': 2,
    'Maret': 3,
    'April': 4,
    'Mei': 5,
    'Juni': 6,
    'Juli': 7,
    'Agustus': 8,
    'September': 9,
    'Oktober': 10,
    'November': 11,
    'Desember': 12
}


def calibrate_province_name(name):
    """Kalibrasi nama provinsi."""

    if pd.isna(name) or name is None or str(name).strip() == "":
        return "UNKNOWN"

    name = str(name).strip().upper()

    if "SUMATERA" in name:
        name = name.replace("SUMATERA", "SUMATRA")

    return PROVINCE_MAPPING.get(name, name)


def parse_created_at(date_val):
    """Parse created_at ke format Indonesia."""

    if pd.isna(date_val):
        return None

    try:

        if isinstance(date_val, str):

            date_val = date_val.strip()

            date_str = (
                date_val.split(' ')[0]
                if ' ' in date_val
                else date_val
            )

            dt = pd.to_datetime(
                date_str,
                dayfirst=True,
                errors='coerce'
            )

        else:

            dt = pd.to_datetime(
                date_val,
                errors='coerce'
            )

        if pd.isna(dt):
            return None

        bulan = {
            1: 'Januari',
            2: 'Februari',
            3: 'Maret',
            4: 'April',
            5: 'Mei',
            6: 'Juni',
            7: 'Juli',
            8: 'Agustus',
            9: 'September',
            10: 'Oktober',
            11: 'November',
            12: 'Desember'
        }

        return f"{dt.day} {bulan[dt.month]} {dt.year}"

    except Exception:
        return None


def parse_indonesian_date(date_str):
    """
    Convert:
    '1 Mei 2026'
    menjadi datetime object.
    """

    if date_str == 'Tanggal Tidak Diketahui':
        return datetime.max

    try:

        parts = date_str.split()

        day = int(parts[0])
        month = MONTH_MAP[parts[1]]
        year = int(parts[2])

        return datetime(year, month, day)

    except Exception:
        return datetime.max


def extract_day_from_date(date_str):
    """Extract day number dari format Indonesia."""

    if date_str == 'Tanggal Tidak Diketahui':
        return "?"

    try:
        return date_str.split()[0]

    except Exception:
        return "?"


class RegionalSummaryView(ctk.CTkFrame):
    """Regional summary view."""

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self.current_results = {}
        self.dates_list = []
        self.active_table_index = 0

        self._setup_ui()

    def _setup_ui(self):

        self.configure(fg_color="transparent")

        main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        ctk.CTkLabel(
            main,
            text="Regional Summary",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.input_section = InputSection(
            main,
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

        self.output_card = ctk.CTkFrame(
            main,
            corner_radius=12
        )
        self.output_card.pack(
            fill="both",
            expand=True,
            pady=3
        )
        self.output_card.pack_forget()

        ctk.CTkLabel(
            self.output_card,
            text="Hasil Analisis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(8, 2)
        )

        self.info_section = InfoSection(self.output_card)

        self.nav_section = NavSection(
            self.output_card,
            on_navigate=self._scroll_to_table
        )

        self.tables_scroll = ctk.CTkScrollableFrame(
            self.output_card,
            fg_color="transparent"
        )
        self.tables_scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=0
        )

        self.tables_container = TablesContainer(
            self.tables_scroll,
            on_table_click=self._on_table_click
        )

        self.scroll_manager = ScrollManager(
            self.tables_container
        )

        self.exporter = ExcelExporter(
            self._get_export_data
        )

        ctk.CTkButton(
            self.output_card,
            text="💾 Save as Excel",
            command=self.exporter.save,
            width=140,
            height=30,
            font=ctk.CTkFont(size=11)
        ).pack(
            anchor="e",
            padx=15,
            pady=(3, 8)
        )

    def _on_file_selected(self, file_path: Path):
        pass

    def _process_data(self):

        file_path = self.input_section.get_file_path()

        if not file_path:
            return

        try:

            df = pd.read_excel(
                file_path,
                engine='openpyxl'
            )

            self._analyze_data(df)

            self._display_results()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Gagal memproses file:\n{str(e)}"
            )

    def _find_column(
        self,
        df,
        keywords,
        exact_match=None
    ):

        if exact_match:

            for col in df.columns:

                col_lower = col.lower().strip()

                for exact in exact_match:

                    if exact.lower() == col_lower:
                        return col

        for col in df.columns:

            col_lower = col.lower().strip()

            if any(k.lower() in col_lower for k in keywords):
                return col

        return None

    def _analyze_data(self, df):

        original_columns = list(df.columns)

        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        col_province = self._find_column(
            df,
            keywords=[
                'province',
                'wilayah',
                'provinsi',
                'daerah',
                'region'
            ]
        )

        col_payment_status = self._find_column(
            df,
            keywords=[
                'status_pembayaran',
                'status'
            ],
            exact_match=[
                'payment_status'
            ]
        )

        col_date = self._find_column(
            df,
            keywords=[
                'created_at',
                'created',
                'tanggal',
                'date',
                'waktu'
            ]
        )

        if not col_province or not col_payment_status:

            raise ValueError(
                f"Kolom tidak ditemukan. "
                f"Tersedia: {original_columns}"
            )

        df[col_payment_status] = (
            df[col_payment_status]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df[col_province] = (
            df[col_province]
            .apply(calibrate_province_name)
        )

        if col_date:

            df['parsed_date'] = (
                df[col_date]
                .apply(parse_created_at)
            )

            if df['parsed_date'].notna().sum() == 0:

                df['parsed_date'] = (
                    'Tanggal Tidak Diketahui'
                )

        else:

            df['parsed_date'] = (
                'Tanggal Tidak Diketahui'
            )

        # ==========================================
        # SORT TANGGAL SECARA KRONOLOGIS
        # ==========================================

        self.dates_list = sorted(
            df['parsed_date'].unique(),
            key=parse_indonesian_date
        )

        self.current_results = {}

        for date_str in self.dates_list:

            date_df = df[
                df['parsed_date'] == date_str
            ].copy()

            leads_summary = (
                date_df
                .groupby(col_province)
                .size()
                .reset_index(name='leads')
            )

            paid_df = date_df[
                date_df[col_payment_status] == 'paid'
            ]

            paid_summary = (
                paid_df
                .groupby(col_province)
                .size()
                .reset_index(name='paid')
            )

            master_df = pd.DataFrame(
                MASTER_PROVINCES,
                columns=[col_province]
            )

            report = pd.merge(
                master_df,
                leads_summary,
                on=col_province,
                how='left'
            )

            report = pd.merge(
                report,
                paid_summary,
                on=col_province,
                how='left'
            )

            report = report.fillna(0).astype({
                'leads': int,
                'paid': int
            })

            self.current_results[date_str] = {
                'dataframe': report,
                'province_col': col_province,
                'total_raw': len(date_df),
                'total_leads': int(report['leads'].sum()),
                'total_paid': int(report['paid'].sum())
            }

    def _display_results(self):

        self.output_card.pack(
            fill="both",
            expand=True,
            pady=3
        )

        total_leads = sum(
            r['total_leads']
            for r in self.current_results.values()
        )

        total_paid = sum(
            r['total_paid']
            for r in self.current_results.values()
        )

        ratio = (
            (total_paid / total_leads * 100)
            if total_leads > 0
            else 0
        )

        date_info = (
            self.dates_list[0]
            if len(self.dates_list) == 1
            else f"{self.dates_list[0]} - {self.dates_list[-1]}"
        )

        self.info_section.update_info(
            date_info,
            total_leads,
            total_paid,
            ratio
        )

        total_raw = sum(
            r['total_raw']
            for r in self.current_results.values()
        )

        self.info_section.update_warning(
            total_raw,
            total_leads
        )

        self.nav_section.create_buttons(
            self.dates_list,
            extract_day_from_date
        )

        self.tables_container.create_tables(
            self.dates_list,
            self.current_results
        )

        self.active_table_index = 0

        self._update_active_state()

    def _on_table_click(self, index):
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):

        if index < 0 or index >= len(self.dates_list):
            return

        self.active_table_index = index

        self._update_active_state()

        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):

        self.tables_container.set_active_table(
            self.active_table_index
        )

        self.nav_section.set_active(
            self.active_table_index
        )

    def _get_export_data(self):
        return self.dates_list, self.current_results

    def _clear_all(self):

        self.output_card.pack_forget()

        self.current_results = {}

        self.dates_list = []

        self.active_table_index = 0

        self.input_section.reset()

        self.info_section.clear()

        self.nav_section.clear()

        self.tables_container.clear()

        self.scroll_manager.reset_scroll()

        self.scroll_manager.cancel_pending()

    def on_show(self):
        pass