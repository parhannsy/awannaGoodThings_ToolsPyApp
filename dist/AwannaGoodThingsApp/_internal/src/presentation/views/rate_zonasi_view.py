"""
View: RateZonasiView
Halaman analisis Rate Zonasi (Delive vs RTS) menggunakan komponen modular
dan format lokalisasi penanggalan Indonesia.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
import pandas as pd

# Impor komponen shared & spesifik fitur rate_zonasi
from src.presentation.components.shared.scroll_manager import ScrollManager
from src.presentation.components.shared.tables_container import TablesContainer

# Catatan: Sesuaikan impor jika kamu menggunakan komponen Input/Info dari shared atau bikin lokal
from src.presentation.components.shared.input_section import InputSection
from src.presentation.components.shared.info_section import InfoSection
from src.presentation.components.shared.nav_section import NavSection
from src.presentation.components.shared.page_header import PageHeader


MASTER_PROVINCES = [
    "BALI", "BANGKA BELITUNG", "BANTEN", "BENGKULU", "DI YOGYAKARTA",
    "DKI JAKARTA", "GORONTALO", "JAMBI", "JAWA BARAT", "JAWA TENGAH",
    "JAWA TIMUR", "KALIMANTAN BARAT", "KALIMANTAN SELATAN", "KALIMANTAN TENGAH",
    "KALIMANTAN TIMUR", "KALIMANTAN UTARA", "KEPULAUAN RIAU", "LAMPUNG",
    "MALUKU", "MALUKU UTARA", "NANGGROE ACEH DARUSSALAM (NAD)",
    "NUSA TENGGARA BARAT (NTB)", "NUSA TENGGARA TIMUR (NTT)", "PAPUA",
    "PAPUA BARAT", "RIAU", "SULAWESI BARAT", "SULAWESI SELATAN",
    "SULAWESI TENGAH", "SULAWESI TENGGARA", "SULAWESI UTARA",
    "SUMATERA BARAT", "SUMATERA SELATAN", "SUMATERA UTARA"
]


class RateZonasiView(ctk.CTkFrame):
    """View orchestrator untuk Fitur Analisis Rate Zonasi (6 Kolom)."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.current_file_path = None
        self.dates_list = []
        self.current_results = {}
        self.active_table_index = 0

        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # Page Title
        self.header = PageHeader(
            master=self,
            title="Rate Zonasi Analytics",
            subtitle="Analisis rasio pengiriman sukses (Delive) vs pengembalian (RTS) per wilayah provinsi secara berkala."
        )

        # Menggunakan input section untuk unggah file
        self.input_section = InputSection(
            self,
            title_label="Belum ada file rate zonasi dipilih",
            browse_text="📁 Pilih File Rate Zonasi",
            process_text="▶ Proses Data",
            clear_text="🧹 Bersihkan",
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

        self.output_card = ctk.CTkFrame(self, fg_color=("gray86", "gray17"), corner_radius=8)
        self.output_card.pack_forget()

        # Section meta info global dan navigasi horizontal tombol tanggal
        self.info_section = InfoSection(self.output_card)
        self.nav_section = NavSection(self.output_card, on_navigate=self._on_nav_click)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.output_card,
            fg_color=("gray90", "gray13"),
            corner_radius=6
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Menggunakan TablesContainer milik rate_zonasi (yang memanggil TableCard 6 Kolom)
        self.tables_container = TablesContainer(
            self.scroll_frame,
            on_table_click=self._on_table_click
        )

        self.scroll_manager = ScrollManager(self.tables_container)

    def on_show(self):
        pass

    def _on_file_selected(self, file_path):
        self.current_file_path = file_path

    def _format_indonesian_date(self, date_str):
        """Helper untuk format judul kartu sesuai standar Rangkuman data {hari}, Tgl Bln Thn."""
        if date_str in ['ALL_DATA', 'TANPA_TANGGAL']:
            return "📁 Rekap Data Zonasi Campuran"

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            hari_indo = hari_list[date_obj.weekday()]
            
            bulan_list = [
                "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            bulan_indo = bulan_list[date_obj.month]
            
            return f"Rangkuman data {hari_indo}, {date_obj.day} {bulan_indo} {date_obj.year}"
        except Exception:
            return f"Tanggal Penjemputan: {date_str}"

    def _process_data(self):
        if not self.current_file_path:
            return

        try:
            # 1. Load File
            if self.current_file_path.suffix.lower() == '.csv':
                df = pd.read_csv(self.current_file_path)
            else:
                df = pd.read_excel(self.current_file_path)

            # Validasi kolom dasar
            if 'Provinsi' not in df.columns or 'Status' not in df.columns:
                raise ValueError("Kolom 'Provinsi' atau 'Status' tidak ditemukan!")

            total_raw = len(df)

            # 2. Pembersihan Data Dasar
            df['prov_clean'] = df['Provinsi'].fillna('UNKNOWN').astype(str).str.strip().str.upper()
            df['status_clean'] = df['Status'].fillna('UNKNOWN').astype(str).str.strip().str.lower()

            # Filter hanya provinsi master yang valid
            df_valid = df[df['prov_clean'].isin(MASTER_PROVINCES)].copy()
            total_leads = len(df_valid)

            # 3. Identifikasi Kolom Tanggal Penjemputan
            date_col = None
            for col in df.columns:
                if col in ['Tanggal Penjemputan', 'Tanggal']:
                    date_col = col
                    break

            if date_col:
                df_valid['date_pure'] = pd.to_datetime(df_valid[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
                df_valid['date_pure'] = df_valid['date_pure'].fillna('TANPA_TANGGAL')
                self.dates_list = sorted([d for d in df_valid['date_pure'].unique() if d != 'TANPA_TANGGAL'])
                if 'TANPA_TANGGAL' in df_valid['date_pure'].unique():
                    self.dates_list.append('TANPA_TANGGAL')
            else:
                df_valid['date_pure'] = 'ALL_DATA'
                self.dates_list = ['ALL_DATA']

            # 4. Core Processing Per Tanggal menggunakan Perulangan Pandas
            self.current_results = {}
            for d_str in self.dates_list:
                df_day = df_valid[df_valid['date_pure'] == d_str]

                # Evaluasi Status Logistik (Silakan sesuaikan keyword string di bawah ini jika berbeda)
                # Delive: Sukses dikirim / Dana cair
                is_delive = df_day['status_clean'].str.contains('dicairkan|selesai|delivered|success', na=False)
                # RTS: Return To Seller / Paket Gagal & Balik ke Gudang
                is_rts = df_day['status_clean'].str.contains('rts|gagal|diretur|ditolak|returned', na=False)

                # Bangun struktur data kosong berbasis MASTER_PROVINCES agar urutan konsisten
                day_payload = []
                
                for prov in MASTER_PROVINCES:
                    df_prov = df_day[df_day['prov_clean'] == prov]
                    
                    total_prov = len(df_prov)
                    delive_count = int(is_delive[df_day['prov_clean'] == prov].sum())
                    rts_count = int(is_rts[df_day['prov_clean'] == prov].sum())

                    # Hitung rasio persentase secara aman
                    ratio_dlv = (delive_count / total_prov * 100) if total_prov > 0 else 0.0
                    ratio_rts = (rts_count / total_prov * 100) if total_prov > 0 else 0.0

                    day_payload.append({
                        "provinsi": prov,
                        "total_raw": total_prov,
                        "delive": delive_count,
                        "ratio_delive": f"{ratio_dlv:.1f}%",
                        "rts": rts_count,
                        "ratio_rts_delive": f"{ratio_rts:.1f}%"
                    })

                self.current_results[d_str] = day_payload

            # 5. Tampilkan Output Card UI
            self.output_card.pack(fill="both", expand=True, pady=(5, 0))

            # Hitung global summary stat untuk InfoSection top bar
            glob_delive = df_valid['status_clean'].str.contains('dicairkan|selesai|delivered|success', na=False).sum()
            glob_ratio = (glob_delive / total_leads * 100) if total_leads > 0 else 0.0
            
            self.info_section.update_info("Global Rate Zonasi", total_leads, int(glob_delive), glob_ratio)
            self.info_section.update_warning(total_raw, total_leads)

            # Generate Tombol Navigasi Tanggal Singkat (Bawah InfoSection)
            def extract_day_from_date(d_val):
                if d_val in ['ALL_DATA', 'TANPA_TANGGAL']: return "Data"
                try: return f"Tgl {datetime.strptime(d_val, '%Y-%m-%d').strftime('%d/%m')}"
                except: return d_val

            self.nav_section.create_buttons(self.dates_list, extract_day_from_date)

            # Render data ke komponen grid khusus rate_zonasi
            self.tables_container.create_tables(self.dates_list, self.current_results)

            self.active_table_index = 0
            self._update_active_state()

        except Exception as e:
            messagebox.showerror("Error Rate Zonasi", f"Gagal menganalisis data rate zonasi:\n{str(e)}")
            self._clear_all()

    def _on_nav_click(self, index):
        self._scroll_to_table(index)

    def _on_table_click(self, index):
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):
        if index < 0 or index >= len(self.dates_list):
            return
        self.active_table_index = index
        self._update_active_state()
        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):
        self.tables_container.set_active_table(self.active_table_index)
        self.nav_section.set_active(self.active_table_index)

    def _clear_all(self):
        self.output_card.pack_forget()
        self.current_file_path = None
        self.dates_list = []
        self.current_results = {}
        self.active_table_index = 0
        
        self.input_section.reset()
        self.info_section.info_label.configure(text="")
        self.info_section.warning_label.configure(text="")
        self.tables_container.clear()