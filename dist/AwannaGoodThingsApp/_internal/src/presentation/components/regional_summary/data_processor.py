"""
Logika Bisnis: RegionalDataProcessor
Mengurus seluruh pembacaan, validasi, pembersihan, dan transformasi data regional summary.
Dipisahkan dari UI untuk mematuhi Single Responsibility Principle.

REVISI:
- Semua provinsi dari MASTER_PROVINCES muncul di hasil, termasuk yang leads 0
- Sorting provinsi mengikuti urutan MASTER_PROVINCES
"""

from datetime import datetime
import pandas as pd
import logging

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


class RegionalDataProcessor:
    """Processor untuk mengolah data mentah summary menjadi payload siap render UI."""

    def __init__(self, master_provinces: list):
        self.master_provinces = [p.upper().strip() for p in master_provinces]
        logger.info(f"MASTER_PROVINCES loaded: {len(self.master_provinces)} provinsi")

    def process_file(self, file_path) -> dict:
        """
        Membaca dan memproses file Excel/CSV.
        Returns:
            dict: Berisi 'dates_list', 'results_by_date', 'global_stats', dan 'warnings'
        """
        logger.info(f"=" * 60)
        logger.info(f"MEMULAI PEMROSESAN FILE: {file_path}")
        logger.info(f"=" * 60)

        # 1. Pembacaan File
        file_ext = file_path.suffix.lower()
        logger.info(f"Format file terdeteksi: {file_ext}")

        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            logger.error(f"GAGAL membaca file: {e}")
            raise

        total_raw = len(df)
        logger.info(f"Total baris mentah: {total_raw}")
        logger.info(f"Kolom tersedia: {list(df.columns)}")

        # 2. Validasi Kolom Wajib
        required = ['created_at', 'province', 'payment_status']
        missing = [col for col in required if col not in df.columns]
        if missing:
            logger.error(f"KOLOM WAJIB TIDAK DITEMUKAN: {missing}")
            raise ValueError(f"Kolom wajib berikut tidak ditemukan: {missing}")

        # 3. Pembersihan Data Dasar
        logger.info("-" * 60)
        logger.info("STEP 3: Pembersihan Data Dasar")

        df['date_pure'] = pd.to_datetime(df['created_at'], errors='coerce').dt.strftime('%Y-%m-%d')
        dates_failed = df['date_pure'].isna().sum()
        if dates_failed > 0:
            logger.warning(f"⚠️ {dates_failed} baris gagal dikonversi tanggal (created_at invalid)")

        df['province_clean'] = df['province'].fillna('UNKNOWN').astype(str).str.strip().str.upper()

        unique_provinces_raw = df['province_clean'].unique()
        logger.info(f"Provinsi unik SEBELUM filter (total {len(unique_provinces_raw)}): {sorted(unique_provinces_raw)[:20]}")
        if len(unique_provinces_raw) > 20:
            logger.info(f"... dan {len(unique_provinces_raw) - 20} provinsi lainnya")

        provinces_not_in_master = set(unique_provinces_raw) - set(self.master_provinces)
        if provinces_not_in_master:
            logger.warning(f"⚠️ Provinsi TIDAK COCOK dengan master ({len(provinces_not_in_master)} unik): {sorted(provinces_not_in_master)}")
        else:
            logger.info("✅ Semua provinsi cocok dengan MASTER_PROVINCES")

        # Filter global untuk menghitung statistik umum
        all_leads_valid = df[df['province_clean'].isin(self.master_provinces)]
        total_leads_valid = len(all_leads_valid)
        
        all_paid_valid = all_leads_valid[all_leads_valid['payment_status'].astype(str).str.strip().str.lower() == 'paid']
        total_paid_valid = len(all_paid_valid)
        
        global_ratio = (total_paid_valid / total_leads_valid * 100) if total_leads_valid > 0 else 0.0

        logger.info(f"Statistik Global — Leads valid: {total_leads_valid}, Paid: {total_paid_valid}, Ratio: {global_ratio:.1f}%")
        logger.info(f"Baris di-drop karena provinsi tidak cocok: {total_raw - total_leads_valid}")

        # 4. Agregasi Per Tanggal
        logger.info("-" * 60)
        logger.info("STEP 4: Agregasi Per Tanggal")

        df_valid = df[df['province_clean'].isin(self.master_provinces)].copy()
        df_valid['is_paid'] = df_valid['payment_status'].astype(str).str.strip().str.lower() == 'paid'

        dates_list = sorted(df['date_pure'].dropna().unique().tolist())
        results_by_date = {}

        for date_str in dates_list:
            df_date = df_valid[df_valid['date_pure'] == date_str]

            total_hari_ini = len(df_date)
            hasil_rows = 0

            if total_hari_ini == 0:
                # Jika tidak ada data sama sekali untuk tanggal ini, buat tabel kosong dari master
                df_result = pd.DataFrame({
                    'province_clean': self.master_provinces,
                    'leads': 0,
                    'paid': 0
                })
                hasil_rows = len(df_result)
            else:
                # Agregasi Leads per provinsi (hanya yang punya data)
                summary = df_date.groupby('province_clean').size().reset_index(name='leads')

                # Agregasi Paid per provinsi (hanya yang punya data paid)
                paid_df = df_date[df_date['is_paid']]
                paid_summary = paid_df.groupby('province_clean').size().reset_index(name='paid')

                # ============================================================
                # REVISI: Gunakan MASTER_PROVINCES sebagai basis agar semua muncul
                # ============================================================
                master_df = pd.DataFrame({'province_clean': self.master_provinces})

                # Merge master dengan summary leads — semua provinsi master tetap ada
                merged = pd.merge(master_df, summary, on='province_clean', how='left').fillna(0)
                merged['leads'] = merged['leads'].astype(int)

                # Merge dengan paid summary
                merged = pd.merge(merged, paid_summary, on='province_clean', how='left').fillna(0)
                merged['paid'] = merged['paid'].astype(int)

                df_result = merged
                hasil_rows = len(df_result)
                # ============================================================

            # ============================================================
            # REVISI: Sorting berdasarkan urutan MASTER_PROVINCES
            # ============================================================
            province_order = {prov: idx for idx, prov in enumerate(self.master_provinces)}
            df_result['sort_order'] = df_result['province_clean'].map(province_order)
            df_result = df_result.sort_values(by='sort_order', na_position='last')
            df_result = df_result.drop(columns=['sort_order'])
            # ============================================================

            log_level = logging.WARNING if hasil_rows == 0 else logging.INFO
            logger.log(log_level, f"📅 {date_str} | Total data hari ini: {total_hari_ini:4d} | Hasil rows: {hasil_rows}")

            results_by_date[date_str] = {
                'dataframe': df_result,
                'province_col': 'province_clean'
            }

        # 5. Bungkus Output secara Rapi
        logger.info("-" * 60)
        logger.info("STEP 5: Finalisasi Output")
        logger.info(f"Total tanggal diproses: {len(dates_list)}")
        logger.info(f"=" * 60)

        return {
            "dates_list": dates_list,
            "results_by_date": results_by_date,
            "global_stats": {
                "total_leads": total_leads_valid,
                "total_paid": total_paid_valid,
                "ratio": global_ratio
            },
            "warnings": {
                "has_warning": total_raw != total_leads_valid,
                "dropped_rows": total_raw - total_leads_valid
            }
        }