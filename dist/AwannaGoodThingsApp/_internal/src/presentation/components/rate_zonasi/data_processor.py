"""
Processor: RateZonasiProcessor
Mengeksekusi kalkulasi analisis logistik Rate Zonasi dengan standardisasi data
meniru total konsep mapping dan pembersihan dari Regional Summary View.
"""

import pandas as pd


class RateZonasiProcessor:
    """Processor untuk mengolah data raw pengiriman menjadi metrik Rate Zonasi."""

    def __init__(self, master_provinces):
        self.master_provinces = master_provinces
        
        # Konsep Mapping: Menerjemahkan variasi teks lapangan agar patuh pada MASTER_PROVINCES
        self.province_mapper = {
            "ACEH": "NANGGROE ACEH DARUSSALAM (NAD)",
            "NUSA TENGGARA BARAT": "NUSA TENGGARA BARAT (NTB)",
            "NUSA TENGGARA TIMUR": "NUSA TENGGARA TIMUR (NTT)",
            "YOGYAKARTA": "DI YOGYAKARTA",
            "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
            "JAKARTA": "DKI JAKARTA",
            "KEPULAUAN RIAU (KEPRI)": "KEPULAUAN RIAU",
            "BANGKA-BELITUNG": "BANGKA BELITUNG"
        }

    def process_file(self, file_path):
        """Memproses file raw pengiriman dengan toleransi mapping terhadap MASTER_PROVINCES."""
        # 1. Pembacaan File adaptif sesuai ekstensi
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Validasi kolom wajib fitur Rate Zonasi kamu
        required_cols = ['Provinsi', 'Status Lastiy', 'Status'] 
        # Catatan: Sesuaikan string kolom status di atas dengan milik data lapanganmu jika berbeda
        
        # Cari kolom status yang tersedia di file CSV kamu
        status_col = None
        for col in ['Status Lastiy', 'Status', 'Status Terakhir dari 3PL']:
            if col in df.columns:
                status_col = col
                break
                
        if 'Provinsi' not in df.columns or not status_col:
            raise ValueError("Struktur kolom file raw pengiriman tidak sesuai standar!")

        total_raw = len(df)

        # ====================================================================
        # REFACTOR: MENIRU TOTAL KONSEP MAPPING & CLEANSING REGIONAL SUMMARY
        # ====================================================================
        # Step A: Jalankan pembersihan dasar (Strip & Upper) persis Regional View
        df['prov_clean'] = df['Provinsi'].fillna('UNKNOWN').astype(str).str.strip().str.upper()
        
        # Step B: Jalankan translasi mapping agar variasi teks CSV lolos uji MASTER_PROVINCES
        df['prov_clean'] = df['prov_clean'].replace(self.province_mapper)

        # Step C: Filter ketat menggunakan .isin() sesuai standardisasi Regional View
        df_valid = df[df['prov_clean'].isin(self.master_provinces)].copy()
        total_leads = len(df_valid)
        dropped_rows = total_raw - total_leads

        # Standardisasi pembersihan kolom status pengiriman
        df_valid['status_clean'] = df_valid[status_col].fillna('UNKNOWN').astype(str).str.strip().str.upper()

        # Tentukan kolom tanggal penjemputan
        date_col = None
        for col in ['Tanggal Penjemputan', 'Tanggal', 'Tanggal Pembuatan']:
            if col in df_valid.columns:
                date_col = col
                break

        if date_col:
            # Ambil tanggal murni YYYY-MM-DD
            df_valid['date_pure'] = pd.to_datetime(df_valid[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
            df_valid['date_pure'] = df_valid['date_pure'].fillna('TANPA_TANGGAL')
            dates_list = sorted([d for d in df_valid['date_pure'].unique() if d != 'TANPA_TANGGAL'])
            if 'TANPA_TANGGAL' in df_valid['date_pure'].unique():
                dates_list.append('TANPA_TANGGAL')
        else:
            df_valid['date_pure'] = 'ALL_DATA'
            dates_list = ['ALL_DATA']

        # 2. Pemrosesan Kalkulasi Metrik Rate Zonasi per Tanggal
        daily_results = {}
        global_total_delive = 0
        global_total_rts = 0

        for d_str in dates_list:
            df_day = df_valid[df_valid['date_pure'] == d_str]
            
            day_data = []
            for prov in self.master_provinces:
                df_prov = df_day[df_day['prov_clean'] == prov]
                row_count = len(df_prov)
                
                if row_count == 0:
                    continue
                
                # Hitung status spesifik zonasi
                # DELIVE: Paket berhasil sampai (bisa disesuaikan dengan keyword data kurirmu seperti 'DELIVERED', 'DICAIRKAN', 'SUKSES')
                delive_count = df_prov['status_clean'].str.contains('DELIVERED|DICAIRKAN|SUKSES|SELESAI', regex=True).sum()
                
                # RTS: Paket retur balik ke gudang (Return To Sender)
                rts_count = df_prov['status_clean'].str.contains('RTS|RETUR|RETURN', regex=True).sum()
                
                ratio_delive = (delive_count / row_count * 100) if row_count > 0 else 0.0
                ratio_rts_delive = (rts_count / delive_count * 100) if delive_count > 0 else 0.0
                
                global_total_delive += delive_count
                global_total_rts += rts_count
                
                day_data.append({
                    "provinsi": prov,
                    "total_raw": row_count,
                    "delive": int(delive_count),
                    "ratio_delive": f"{ratio_delive:.1f}%",
                    "rts": int(rts_count),
                    "ratio_rts_delive": f"{ratio_rts_delive:.1f}%"
                })
            
            daily_results[d_str] = day_data

        # 3. Penyusunan Payload Output Global Statis
        global_ratio_delive = (global_total_delive / total_leads * 100) if total_leads > 0 else 0.0
        global_ratio_rts = (global_total_rts / global_total_delive * 100) if global_total_delive > 0 else 0.0

        return {
            "dates_list": dates_list,
            "daily_results": daily_results,
            "global_stats": {
                "total_raw_processed": total_leads,
                "total_delive": global_total_delive,
                "ratio_delive": global_ratio_delive,
                "total_rts": global_total_rts,
                "ratio_rts_delive": global_ratio_rts
            },
            "warnings": {
                "has_warning": dropped_rows > 0,
                "dropped_rows": dropped_rows
            }
        }