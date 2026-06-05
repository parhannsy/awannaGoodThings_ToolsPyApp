"""
Data Processor FLIK
Desktop version adapted from Google Colab workflow.
"""

import os
import re
import logging
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional, Dict, List, Any
from datetime import datetime

import pandas as pd

# Setup logging ke terminal secara profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("DataProcessorFLIK")

RE_WHITESPACE = re.compile(r'\s+')
RE_NON_WORD = re.compile(r'[^\w\s]')


class DataProcessorFLIK:

    CURRENT_DIR = Path(__file__).resolve().parent
    REFERENCE_FILE = CURRENT_DIR / "references" / "referensi daerah.xlsx"

    @staticmethod
    def generate_default_filename():
        return f"processed_flik_{datetime.now():%Y%m%d_%H%M%S}.xlsx"

    @staticmethod
    def load_file_safely(file_path: str) -> Optional[pd.DataFrame]:
        logger.info(f"Mencoba membaca file: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            for enc in ["utf-8", "iso-8859-1", "cp1252"]:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=enc,
                        low_memory=False
                    ).fillna("")
                    logger.info(f"Berhasil membaca CSV dengan encoding: {enc}")
                    return df
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    logger.warning(f"Gagal membaca CSV dengan encoding {enc}, mencoba encoding lain... Error: {e}")
                    continue
            raise ValueError(f"Gagal membaca CSV setelah mencoba beberapa encoding: {file_path}")

        elif ext in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(file_path).fillna("")
                logger.info("Berhasil membaca file Excel.")
                return df
            except Exception as e:
                logger.error(f"Eror saat membaca file Excel: {str(e)}")
                raise e

        logger.error(f"Format file tidak didukung: {ext}")
        return None

    @staticmethod
    def normalize_text(text: Any) -> str:
        if text is None or pd.isna(text):
            return ""
        text = str(text).lower().strip()
        text = RE_WHITESPACE.sub(" ", text)
        text = RE_NON_WORD.sub("", text)
        return text

    @staticmethod
    def normalize_city_name(city_name: Any) -> str:
        city = DataProcessorFLIK.normalize_text(city_name)
        for r in ["kabupaten", "kab", "kota administrasi", "kota adm", "kota"]:
            city = city.replace(r, "")
        return RE_WHITESPACE.sub(" ", city).strip()

    @staticmethod
    def calculate_similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def get_auto_pcs(product_name: str, price: Any) -> int:
        try:
            p_price = float(price)
            p_name = DataProcessorFLIK.normalize_text(product_name)

            if "kabel" in p_name or "charger" in p_name:
                if 79000 <= p_price <= 115000:
                    return 2
                elif p_price >= 119000:
                    return 4
                return 1

            if 99000 <= p_price <= 159000:
                return 2
            elif 160000 <= p_price <= 200000:
                return 4

            return 1
        except Exception as e:
            logger.debug(f"Gagal menghitung auto pcs untuk {product_name} (Price: {price}): {e}")
            return 1

    @staticmethod
    def build_advanced_ref_map(df_ref: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
        logger.info("Membangun advanced reference map untuk area...")
        ref_dict = {}

        for idx, row in enumerate(df_ref.to_dict("records")):
            try:
                keys = list(row.keys())

                if len(keys) < 2:
                    continue

                city_raw = str(row[keys[0]]).strip()
                dist_raw = str(row[keys[1]]).strip()

                city_norm = DataProcessorFLIK.normalize_city_name(city_raw)
                dist_norm = DataProcessorFLIK.normalize_text(dist_raw)

                if not dist_norm:
                    continue

                ref_dict.setdefault(dist_norm, []).append({
                    "city_original": city_raw,
                    "city_normalized": city_norm,
                    "district_original": dist_raw
                })
            except Exception as e:
                logger.error(f"Eror pada baris referensi ke-{idx}: {str(e)} | Data: {row}")
                raise e

        logger.info(f"Reference map selesai dibangun. Total kecamatan terdaftar: {len(ref_dict)}")
        return ref_dict

    @staticmethod
    def validate_area(raw_dist: Any, raw_city: Any, ref_map: dict) -> str:
        notebook_dist = DataProcessorFLIK.normalize_text(raw_dist)
        norm_city = DataProcessorFLIK.normalize_city_name(raw_city)

        if notebook_dist not in ref_map:
            return str(raw_city)

        candidates = ref_map[notebook_dist]

        if len(candidates) == 1:
            return candidates[0]["city_original"]

        best_match = None
        best_score = 0.0

        for candidate in candidates:
            candidate_city = candidate["city_normalized"]

            if candidate_city in norm_city or norm_city in candidate_city:
                score = 1.0
            else:
                score = DataProcessorFLIK.calculate_similarity(
                    norm_city,
                    candidate_city
                )

            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= 0.65 and best_match is not None:
            return best_match["city_original"]

        return str(raw_city)

    @staticmethod
    def get_glasses_recommendation(notes: Any) -> str:
        try:
            if not notes or pd.isna(notes):
                return ""
            
            age_str = "".join(filter(str.isdigit, str(notes)))
            if not age_str:
                return ""

            age = int(age_str)

            if 40 <= age <= 42: return "+1.00"
            if 43 <= age <= 47: return "+1.25"
            if 48 <= age <= 49: return "+1.75"
            if 50 <= age <= 54: return "+2.00"
            if 55 <= age <= 57: return "+2.50"
            if 58 <= age <= 59: return "+2.25"
            if 60 <= age <= 64: return "+3.00"
            if age >= 65: return "+3.50"

        except Exception as e:
            logger.warning(f"Gagal memproses rekomendasi kacamata pada notes '{notes}': {e}")

        return ""

    @classmethod
    def process(cls, input_file: str, output_file: str) -> dict:
        logger.info("=== Memulai Proses Transformasi FLIK ===")
        
        df_raw = cls.load_file_safely(input_file)
        if df_raw is None:
            raise ValueError("File raw tidak dapat dibaca atau kosong.")

        if not os.path.exists(cls.REFERENCE_FILE):
            logger.error(f"File referensi tidak ditemukan di path: {cls.REFERENCE_FILE}")
            raise FileNotFoundError(f"File referensi tidak ditemukan di: {cls.REFERENCE_FILE}")

        df_ref = cls.load_file_safely(str(cls.REFERENCE_FILE))
        if df_ref is None:
            raise ValueError("File referensi area rusak atau tidak bisa dibaca.")

        ref_map = cls.build_advanced_ref_map(df_ref)
        output_data = []

        records = df_raw.to_dict("records")
        total_data = len(records)
        logger.info(f"Total data yang akan diproses: {total_data} baris.")

        # PERBAIKAN LOGIKA MENTOR: Mencegah nilai minus akibat pembulatan round() pada data kecil
        count_p = int(total_data * 0.25)
        count_d = int(total_data * 0.33)
        count_a = max(0, total_data - count_p - count_d)

        constants_pool = (
            ["(P)"] * count_p +
            ["(D)"] * count_d +
            ["(A)"] * count_a
        )
        
        # Jaga-jaga jika total pool masih kurang dari total data karena penyesuaian ukuran
        while len(constants_pool) < total_data:
            constants_pool.append("(A)")

        # Loop pemrosesan data utama
        for idx, row in enumerate(records):
            try:
                # Log progress berkala setiap 50 baris agar terminal tidak banjir tapi tetap terpantau
                if idx % 50 == 0 or idx == total_data - 1:
                    logger.info(f"Memproses baris ke-{idx + 1}/{total_data}...")

                phone = str(row.get("phone", "")).replace(".0", "").strip()

                if phone.startswith("0"):
                    phone = "62" + phone[1:]
                elif phone and not phone.startswith("62"):
                    phone = "62" + phone

                product = str(row.get("product", ""))
                product_price = row.get("product_price", 0)

                pcs = cls.get_auto_pcs(product, product_price)
                recom = cls.get_glasses_recommendation(row.get("notes", ""))

                valid_city = cls.validate_area(
                    row.get("subdistrict", ""),
                    row.get("city", ""),
                    ref_map
                )

                clean_name = " ".join([
                    w.capitalize()
                    for w in cls.normalize_text(product).split()
                    if len(w) > 3
                ])

                current_constant = constants_pool[idx]

                output_data.append({
                    "Kode Warehouse": "AWANNA",
                    "Nama Pelanggan": str(row.get("name", "")).split("(")[0].strip().title(),
                    "No HP Pelanggan (62)": phone,
                    "No HP Pelanggan (8)": phone.replace("62", "", 1) if phone.startswith("62") else phone,
                    "Alamat: Lengkap": row.get("address", ""),
                    "Alamat: Provinsi": row.get("province", ""),
                    "Alamat: Kota": valid_city,
                    "Alamat: Kecamatan": row.get("subdistrict", ""),
                    "Alamat: Kelurahan": "",
                    "Alamat: Kode Pos": row.get("zip", ""),
                    "Alamat: Catatan Kurir": "Hubungi konsumen sebelum dikirim",
                    "Total Nilai Barang / Total Nilai COD": row.get("gross_revenue", ""),
                    "Panjang Barang (cm)": 6,
                    "Lebar Barang (cm)": 8,
                    "Tinggi Barang (cm)": 10,
                    "Berat (kg)": 1,
                    "Nama Produk 1": f"{current_constant} - {clean_name} - ({recom if recom else '-'}) - ({pcs} pcs)",
                    "Nama Produk 2": clean_name,
                    "product_price": product_price,
                    "Metode Pembayaran": str(row.get("payment_method", "")).upper()
                })

            except Exception as e:
                # Menangkap letak pasti baris dan kolom yang menyebabkan eror
                logger.critical(f"CRASH TERJADI pada baris data ke-{idx + 1}!")
                logger.critical(f"Detail Data Baris: {row}")
                logger.critical(f"Pesan Eror: {str(e)}")
                raise e

        try:
            logger.info("Menyusun data ke dalam DataFrame...")
            result = pd.DataFrame(output_data)
            
            logger.info(f"Menyimpan file hasil ke: {output_file}")
            result.to_excel(output_file, index=False)
            
            logger.info("=== Proses Transformasi FLIK Selesai dengan Sukses ===")
            return {
                "success": True,
                "total_data": len(result),
                "output_file": output_file
            }
        except Exception as e:
            logger.critical(f"Gagal menyimpan file Excel output: {str(e)}")
            raise e