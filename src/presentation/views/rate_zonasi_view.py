"""
View: RateZonasiView
Halaman analisis Rate Zonasi (Delive vs RTS) menggunakan komponen internal (standalone).
Format lokalisasi penanggalan Indonesia.

REVISI:
- Pengecekan provinsi berlapis dengan logging detail
- Semua provinsi dari MASTER_PROVINCES muncul di hasil (termasuk yang leads 0)
- Sorting provinsi mengikuti urutan MASTER_PROVINCES
- Padding dihapus karena sudah diatur oleh basepage
- Komponen dipisah ke file-file terpisah
"""

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
import pandas as pd
import logging

from src.presentation.components.rate_zonasi.constant import MASTER_PROVINCES, STATUS_DELIVE, STATUS_RTS, COLORS, FONTS
from src.presentation.components.rate_zonasi.province_normalizer import normalize_province
from src.presentation.components.rate_zonasi.input_section import RateZonasiInputSection
from src.presentation.components.rate_zonasi.info_bar import RateZonasiInfoBar
from src.presentation.components.rate_zonasi.nav_bar import RateZonasiNavBar
from src.presentation.components.rate_zonasi.tables_container import RateZonasiTablesContainer
from src.presentation.components.rate_zonasi.scroll_manager import RateZonasiScrollManager

# ============================================================
# LOGGING SETUP
# ============================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s] %(asctime)s — %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# ============================================================
# VIEW UTAMA
# ============================================================

class RateZonasiView(ctk.CTkFrame):
    """View orchestrator untuk Fitur Analisis Rate Zonasi (6 Kolom) - Per Bulan."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.current_file_path = None
        self.months_list = []
        self.current_results = {}
        self.active_table_index = 0

        self._setup_ui()

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # =====================================================
        # PAGE HEADER
        # =====================================================

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header_frame.pack(
            fill="x",
            pady=(0, 16)
        )

        ctk.CTkLabel(
            header_frame,
            text="📊 Rate Zonasi Analytics",
            font=FONTS["title"],
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            pady=(0, 4)
        )

        ctk.CTkLabel(
            header_frame,
            text=(
                "Analisis rasio pengiriman sukses "
                "(Delive: Dicairkan + Terkirim) "
                "vs pengembalian "
                "(RTS: Dikembalikan) "
                "per wilayah provinsi per bulan."
            ),
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"]
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        # =====================================================
        # INPUT SECTION
        # =====================================================

        self.input_section = RateZonasiInputSection(
            self,
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

        self.input_section.pack(
            fill="x",
            pady=(0, 16)
        )

        # =====================================================
        # OUTPUT CARD
        # =====================================================

        self.output_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12
        )

        # =====================================================
        # INFO BAR
        # =====================================================

        self.info_bar = RateZonasiInfoBar(
            self.output_card
        )

        self.info_bar.pack(
            fill="x",
            padx=16,
            pady=(16, 12)
        )

        # =====================================================
        # NAV BAR
        # =====================================================

        self.nav_bar = RateZonasiNavBar(
            self.output_card,
            on_navigate=self._on_nav_click
        )

        self.nav_bar.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        # =====================================================
        # SCROLL FRAME
        # =====================================================

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.output_card,
            fg_color=COLORS["bg_table"],
            corner_radius=8
        )

        self.scroll_frame.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 16)
        )

        # =====================================================
        # TABLES CONTAINER
        # =====================================================

        self.tables_container = RateZonasiTablesContainer(
            self.scroll_frame,
            on_table_click=self._on_table_click
        )

        self.tables_container.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.scroll_manager = RateZonasiScrollManager(
            self.tables_container
        )

    def on_show(self):
        pass

    # ========================================================
    # EVENT HANDLERS
    # ========================================================

    def _on_file_selected(self, file_path):
        self.current_file_path = file_path

    def _on_nav_click(self, index):
        self._scroll_to_table(index)

    def _on_table_click(self, index):
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):
        if index < 0 or index >= len(self.months_list):
            return
        self.active_table_index = index
        self._update_active_state()
        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):
        self.tables_container.set_active_table(self.active_table_index)
        self.nav_bar.set_active(self.active_table_index)

    # ========================================================
    # CORE PROCESSING - DENGAN PENGECEKAN BERLAPIS
    # ========================================================

    def _process_data(self):
        if not self.current_file_path:
            messagebox.showwarning("File Belum Dipilih", "Silakan pilih file data pengiriman terlebih dahulu.")
            return

        try:
            # ============================================================
            # STEP 1: PEMBACAAN FILE
            # ============================================================
            logger.info("=" * 60)
            logger.info(f"MEMULAI PEMROSESAN FILE: {self.current_file_path}")
            logger.info("=" * 60)

            suffix = self.current_file_path.suffix.lower()
            logger.info(f"Format file terdeteksi: {suffix}")

            if suffix == ".csv":
                df = pd.read_csv(self.current_file_path)
            elif suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(self.current_file_path)
            else:
                raise ValueError(f"Format file '{suffix}' tidak didukung. Gunakan .csv, .xlsx, atau .xls")

            total_raw = len(df)
            logger.info(f"Total baris mentah: {total_raw}")
            logger.info(f"Kolom tersedia: {list(df.columns)}")

            # ============================================================
            # STEP 2: VALIDASI KOLOM WAJIB
            # ============================================================
            required_cols = ["Provinsi", "Status"]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                logger.error(f"KOLOM WAJIB TIDAK DITEMUKAN: {missing}")
                raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

            # ============================================================
            # STEP 3: PEMBERSIHAN DATA DASAR
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 3: Pembersihan Data Dasar")

            df["prov_clean"] = df["Provinsi"].apply(normalize_province)
            df["status_clean"] = df["Status"].fillna("UNKNOWN").astype(str).str.strip().str.lower()

            # --- LAPIS 1: Analisis Provinsi Sebelum Filter ---
            unique_provinces_raw = df["prov_clean"].unique()
            logger.info(f"Provinsi unik SEBELUM filter (total {len(unique_provinces_raw)}): {sorted(unique_provinces_raw)[:20]}")
            if len(unique_provinces_raw) > 20:
                logger.info(f"... dan {len(unique_provinces_raw) - 20} provinsi lainnya")

            # Identifikasi provinsi yang tidak cocok dengan master
            provinces_not_in_master = set(unique_provinces_raw) - set(MASTER_PROVINCES)
            if provinces_not_in_master:
                logger.warning(f"⚠️ Provinsi TIDAK COCOK dengan master ({len(provinces_not_in_master)} unik): {sorted(provinces_not_in_master)}")
                # Simpan detail untuk ditampilkan di UI
                dropped_details = f"{len(provinces_not_in_master)} provinsi tidak valid"
            else:
                logger.info("✅ Semua provinsi cocok dengan MASTER_PROVINCES")
                dropped_details = None

            # ============================================================
            # STEP 4: FILTER STATUS RELEVAN (DELIVE + RTS)
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 4: Filter Status Relevan")

            is_delive = df["status_clean"].isin(STATUS_DELIVE)
            is_rts = df["status_clean"].isin(STATUS_RTS)
            is_relevant = is_delive | is_rts

            # Logging status unik untuk debugging
            unique_statuses = df["status_clean"].unique()
            logger.info(f"Status unik dalam file ({len(unique_statuses)}): {sorted(unique_statuses)[:20]}")
            if len(unique_statuses) > 20:
                logger.info(f"... dan {len(unique_statuses) - 20} status lainnya")

            irrelevant_count = (~is_relevant).sum()
            logger.info(f"Data dengan status tidak relevan: {irrelevant_count}")

            df_relevant = df[is_relevant].copy()
            logger.info(f"Data setelah filter status: {len(df_relevant)}")

            # ============================================================
            # STEP 5: FILTER PROVINSI VALID
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 5: Filter Provinsi Valid")

            df_valid = df_relevant[df_relevant["prov_clean"].isin(MASTER_PROVINCES)].copy()
            total_leads = len(df_valid)

            logger.info(f"Data valid (provinsi cocok + status relevan): {total_leads}")
            logger.info(f"Baris di-drop karena provinsi tidak cocok: {len(df_relevant) - len(df_valid)}")
            logger.info(f"Total baris di-drop (semua alasan): {total_raw - total_leads}")

            if total_leads == 0:
                raise ValueError("Tidak ada data valid setelah filtering. Periksa nama provinsi dan status.")

            # --- LAPIS 2: Analisis Provinsi Setelah Filter ---
            unique_provinces_valid = df_valid["prov_clean"].unique()
            logger.info(f"Provinsi unik SETELAH filter: {sorted(unique_provinces_valid)}")

            # ============================================================
            # STEP 6: IDENTIFIKASI KOLOM TANGGAL & GROUPING PER BULAN
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 6: Identifikasi Kolom Tanggal")

            date_col = None
            for col in df.columns:
                if col.lower() in ["tanggal penjemputan", "tanggal", "tanggal pembuatan", "date", "created_at"]:
                    date_col = col
                    break

            if date_col:
                logger.info(f"Kolom tanggal terdeteksi: '{date_col}'")
                df_valid["date_parsed"] = pd.to_datetime(df_valid[date_col], errors="coerce")
                dates_failed = df_valid["date_parsed"].isna().sum()
                if dates_failed > 0:
                    logger.warning(f"⚠️ {dates_failed} baris gagal dikonversi tanggal")

                df_valid["month_pure"] = df_valid["date_parsed"].dt.to_period("M").astype(str)
                df_valid["month_pure"] = df_valid["month_pure"].fillna("TANPA_BULAN")

                self.months_list = sorted([m for m in df_valid["month_pure"].unique() if m != "TANPA_BULAN"])
                if "TANPA_BULAN" in df_valid["month_pure"].unique():
                    self.months_list.append("TANPA_BULAN")
                logger.info(f"Bulan unik ditemukan: {self.months_list}")
            else:
                logger.warning("⚠️ Tidak ada kolom tanggal yang cocok. Data akan digabung jadi satu.")
                df_valid["month_pure"] = "ALL_DATA"
                self.months_list = ["ALL_DATA"]

            # ============================================================
            # STEP 7: CORE PROCESSING PER BULAN DENGAN MASTER_MERGE
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 7: Agregasi Per Bulan")

            self.current_results = {}

            for m_str in self.months_list:
                df_month = df_valid[df_valid["month_pure"] == m_str]

                total_bulan_ini = len(df_month)
                logger.info(f"📅 {m_str} | Total data bulan ini: {total_bulan_ini}")

                # Re-evaluate status untuk subset bulan ini
                month_is_delive = df_month["status_clean"].isin(STATUS_DELIVE)
                month_is_rts = df_month["status_clean"].isin(STATUS_RTS)

                # --- LAPIS 3: Agregasi dengan MASTER_MERGE ---
                # Buat DataFrame master dengan semua provinsi
                master_df = pd.DataFrame({"provinsi": MASTER_PROVINCES})

                # Agregasi per provinsi dari data aktual
                if total_bulan_ini == 0:
                    # Fallback: semua provinsi dengan nilai 0
                    summary_df = master_df.copy()
                    summary_df["total_raw"] = 0
                    summary_df["delive"] = 0
                    summary_df["rts"] = 0
                    logger.warning(f"⚠️ {m_str}: Tidak ada data, menggunakan fallback (semua 0)")
                else:
                    # Group by provinsi untuk count
                    prov_counts = df_month.groupby("prov_clean").size().reset_index(name="total_raw")

                    # Count delive per provinsi
                    delive_counts = df_month[month_is_delive].groupby("prov_clean").size().reset_index(name="delive")

                    # Count rts per provinsi
                    rts_counts = df_month[month_is_rts].groupby("prov_clean").size().reset_index(name="rts")

                    # Merge ke master (LEFT JOIN agar semua provinsi master tetap ada)
                    summary_df = pd.merge(master_df, prov_counts, left_on="provinsi", right_on="prov_clean", how="left")
                    summary_df = pd.merge(summary_df, delive_counts, on="prov_clean", how="left")
                    summary_df = pd.merge(summary_df, rts_counts, on="prov_clean", how="left")

                    # Bersihkan kolom duplikat dan fillna
                    summary_df = summary_df.drop(columns=["prov_clean"], errors="ignore")
                    summary_df["total_raw"] = summary_df["total_raw"].fillna(0).astype(int)
                    summary_df["delive"] = summary_df["delive"].fillna(0).astype(int)
                    summary_df["rts"] = summary_df["rts"].fillna(0).astype(int)

                # --- LAPIS 4: Sorting berdasarkan urutan MASTER_PROVINCES ---
                province_order = {prov: idx for idx, prov in enumerate(MASTER_PROVINCES)}
                summary_df["sort_order"] = summary_df["provinsi"].map(province_order)
                summary_df = summary_df.sort_values(by="sort_order", na_position="last")
                summary_df = summary_df.drop(columns=["sort_order"])

                # Konversi ke format payload
                month_payload = []
                for _, row in summary_df.iterrows():
                    total_prov = int(row["total_raw"])
                    delive_count = int(row["delive"])
                    rts_count = int(row["rts"])

                    ratio_dlv = (delive_count / total_prov * 100) if total_prov > 0 else 0.0
                    ratio_rts = (rts_count / total_prov * 100) if total_prov > 0 else 0.0

                    month_payload.append({
                        "provinsi": row["provinsi"],
                        "total_raw": total_prov,
                        "delive": delive_count,
                        "ratio_delive": f"{ratio_dlv:.1f}%",
                        "rts": rts_count,
                        "ratio_rts_delive": f"{ratio_rts:.1f}%"
                    })

                self.current_results[m_str] = month_payload
                logger.info(f"   ✅ {m_str}: {len(month_payload)} provinsi dihasilkan")

            # ============================================================
            # STEP 8: TAMPILKAN OUTPUT
            # ============================================================
            logger.info("-" * 60)
            logger.info("STEP 8: Finalisasi Output")

            self.output_card.pack(fill="both", expand=True)

            # Global Summary
            glob_delive = int(df_valid["status_clean"].isin(STATUS_DELIVE).sum())
            glob_ratio = (glob_delive / total_leads * 100) if total_leads > 0 else 0.0

            self.info_bar.update_info(total_leads, glob_delive, glob_ratio)
            self.info_bar.update_warning(total_raw, total_leads, dropped_details)

            # Nav Buttons
            def extract_month_label(m_val):
                if m_val in ["ALL_DATA", "TANPA_BULAN"]:
                    return "Data"
                try:
                    date_obj = datetime.strptime(m_val, "%Y-%m")
                    bulan_list = [
                        "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
                    ]
                    bulan_singkat = bulan_list[date_obj.month]
                    return f"{bulan_singkat} {date_obj.year}"
                except:
                    return m_val

            self.nav_bar.create_buttons(self.months_list, extract_month_label)

            # Render Tables
            self.tables_container.create_tables(self.months_list, self.current_results)

            self.active_table_index = 0
            self._update_active_state()

            logger.info(f"Total bulan diproses: {len(self.months_list)}")
            logger.info("=" * 60)

            messagebox.showinfo(
                "Proses Selesai",
                f"✅ Berhasil memproses {total_leads:,} data valid dari {total_raw:,} total data.\n"
                f"📅 {len(self.months_list)} bulan unik ditemukan."
            )

        except Exception as e:
            logger.error(f"GAGAL menganalisis data: {e}")
            messagebox.showerror("Error Rate Zonasi", f"Gagal menganalisis data:\n{str(e)}")
            self._clear_all()

    def _clear_all(self):
        self.output_card.pack_forget()
        self.current_file_path = None
        self.months_list = []
        self.current_results = {}
        self.active_table_index = 0

        self.input_section.reset()
        self.info_bar.clear()
        self.nav_bar.clear()
        self.tables_container.clear()