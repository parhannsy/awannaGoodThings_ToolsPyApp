"""
View: RateZonasiView
Halaman analisis delivery vs RTS per provinsi.
"""

from tkinter import messagebox

import pandas as pd

from src.presentation.views.base import BasePageView


# Reuse master data dari regional_summary
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
    'ACEH': ACEH_NAME, 'NAD': ACEH_NAME, 'NANGGROE ACEH DARUSSALAM (NAD)': ACEH_NAME,
    'YOGYAKARTA': YOGYA_NAME, 'JOGJA': YOGYA_NAME, 'DIY': YOGYA_NAME,
    'JAKARTA': JAKARTA_NAME,
    'NTB': 'NUSA TENGGARA BARAT (NTB)', 'NTT': 'NUSA TENGGARA TIMUR (NTT)',
    'KEP RIAU': 'KEPULAUAN RIAU', 'KEP. RIAU': 'KEPULAUAN RIAU',
    'BANGKA': 'BANGKA BELITUNG', 'BABEL': 'BANGKA BELITUNG',
    'SULSEL': 'SULAWESI SELATAN', 'SULTENG': 'SULAWESI TENGAH',
    'SULTRA': 'SULAWESI TENGGARA', 'SULUT': 'SULAWESI UTARA',
    'KALBAR': 'KALIMANTAN BARAT', 'KALSEL': 'KALIMANTAN SELATAN',
    'KALTENG': 'KALIMANTAN TENGAH', 'KALTIM': 'KALIMANTAN TIMUR',
    'KALUT': 'KALIMANTAN UTARA',
}


def calibrate_province_name(name):
    """Kalibrasi nama provinsi."""
    if pd.isna(name) or name is None or str(name).strip() == "":
        return "UNKNOWN"
    name = str(name).strip().upper()
    if "SUMATERA" in name:
        name = name.replace("SUMATERA", "SUMATRA")
    return PROVINCE_MAPPING.get(name, name)


class RateZonasiView(BasePageView):
    """
    Rate Zonasi — extend BasePageView.
    Analisis delivery vs RTS per provinsi.
    """

    PAGE_TITLE = "Rate Zonasi"
    OUTPUT_TITLE = "Hasil Analisis Zonasi"
    HAS_DATE_NAVIGATION = False   # Single summary, tidak perlu nav tanggal
    HAS_EXCEL_EXPORT = True

    # Status yang dianggap "delivered" dan "rts"
    DELIVERED_STATUS = ['delivered', 'completed', 'done', 'success', 'terkirim']
    RTS_STATUS = ['rts', 'return_to_sender', 'returned', 'failed', 'gagal', 'batal']

    def _find_column(self, df, keywords, exact_match=None):
        """Find column dengan prioritas exact match."""
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

    def _calibrate_delivery_status(self, status):
        """Kalibrasi status pengiriman ke delivered/rts/other."""
        if pd.isna(status):
            return 'other'
        
        status = str(status).strip().lower()
        
        if status in self.DELIVERED_STATUS:
            return 'delivered'
        elif status in self.RTS_STATUS:
            return 'rts'
        else:
            return 'other'

    def _analyze_data(self, df):
        """Analyze dataframe — delivery vs RTS per provinsi."""
        original_columns = list(df.columns)
        df.columns = [str(col).strip().lower() for col in df.columns]

        # Cari kolom
        col_province = self._find_column(
            df,
            keywords=['province', 'wilayah', 'provinsi', 'daerah', 'region']
        )
        col_status = self._find_column(
            df,
            keywords=['status', 'delivery_status', 'shipping_status', 
                     'status_pengiriman', 'order_status', 'delivery'],
            exact_match=['delivery_status']
        )

        if not col_province or not col_status:
            raise ValueError(
                f"Kolom tidak ditemukan.\n"
                f"Perlu kolom provinsi dan status pengiriman.\n"
                f"Tersedia: {original_columns}"
            )

        # Process provinsi
        df[col_province] = df[col_province].apply(calibrate_province_name)

        # Process status — kalibrasi ke delivered/rts/other
        df['calibrated_status'] = df[col_status].apply(self._calibrate_delivery_status)

        # Agregasi per provinsi
        province_summary = df.groupby(col_province).size().reset_index(name='total_orders')
        
        delivered_df = df[df['calibrated_status'] == 'delivered']
        delivered_summary = delivered_df.groupby(col_province).size().reset_index(name='delivered')
        
        rts_df = df[df['calibrated_status'] == 'rts']
        rts_summary = rts_df.groupby(col_province).size().reset_index(name='rts')

        # Merge dengan master provinces
        master_df = pd.DataFrame(MASTER_PROVINCES, columns=[col_province])
        report = pd.merge(master_df, province_summary, on=col_province, how='left')
        report = pd.merge(report, delivered_summary, on=col_province, how='left')
        report = pd.merge(report, rts_summary, on=col_province, how='left')

        report = report.fillna(0).astype({
            'total_orders': int,
            'delivered': int,
            'rts': int
        })

        # Hitung persentase
        report['delivery_pct'] = report.apply(
            lambda row: (row['delivered'] / row['total_orders'] * 100) 
            if row['total_orders'] > 0 else 0,
            axis=1
        )
        report['rts_pct'] = report.apply(
            lambda row: (row['rts'] / row['total_orders'] * 100)
            if row['total_orders'] > 0 else 0,
            axis=1
        )

        # Simpan hasil
        self.current_results = {
            'dataframe': report,
            'province_col': col_province,
            'total_orders': int(report['total_orders'].sum()),
            'total_delivered': int(report['delivered'].sum()),
            'total_rts': int(report['rts'].sum()),
            'overall_delivery_pct': (report['delivered'].sum() / report['total_orders'].sum() * 100)
            if report['total_orders'].sum() > 0 else 0
        }

    def _display_results(self):
        """Display hasil analysis zonasi."""
        self.output_card.pack(fill="both", expand=True, pady=3)

        result = self.current_results
        df = result['dataframe']
        col_province = result['province_col']

        # Update info section
        self.info_section.update_info(
            date_info=None,  # Tidak ada tanggal untuk single summary
            total_leads=result['total_orders'],
            total_paid=result['total_delivered'],
            ratio=result['overall_delivery_pct']
        )

        # Custom info text untuk zonasi
        self.info_section.info_label.configure(
            text=f"Total Order: {result['total_orders']} | "
                 f"Delivered: {result['total_delivered']} | "
                 f"RTS: {result['total_rts']} | "
                 f"Delivery Rate: {result['overall_delivery_pct']:.1f}%"
        )

        # Warning kalau ada data tidak masuk master
        total_raw = len(df)
        total_mapped = result['total_orders']
        if total_raw != total_mapped:
            diff = total_raw - total_mapped
            self.info_section.warning_label.configure(
                text=f"[!] Warning: Ada {diff} data provinsi yang tidak masuk Master List."
            )
        else:
            self.info_section.warning_label.configure(text="")

        # Buat single table (tidak perlu nav section karena single summary)
        # Override tables_container untuk single table
        self.tables_container.create_single_table(
            df=df,
            col_province=col_province,
            columns=['total_orders', 'delivered', 'rts', 'delivery_pct', 'rts_pct'],
            headers=['PROVINCE', 'TOTAL', 'DELIVERED', 'RTS', 'DELIVERY %', 'RTS %']
        )

        # Set active (hanya 1 table)
        self.active_table_index = 0
        self.tables_container.set_active_table(0)

    def _get_export_data(self):
        """Return data untuk export."""
        # Format untuk ExcelExporter
        return ['Summary'], self.current_results