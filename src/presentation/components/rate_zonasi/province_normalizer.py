"""
Normalisasi nama provinsi dari input raw ke master list.
"""

import re
from difflib import get_close_matches
import pandas as pd

from .constant import MASTER_PROVINCES

PROVINCE_ALIASES = {
    "ACEH": "NANGGROE ACEH DARUSSALAM (NAD)",
    "NAD": "NANGGROE ACEH DARUSSALAM (NAD)",
    "NANGROE ACEH DARUSSALAM": "NANGGROE ACEH DARUSSALAM (NAD)",
    "JAKARTA": "DKI JAKARTA",
    "DKI": "DKI JAKARTA",
    "DAERAH KHUSUS IBUKOTA JAKARTA": "DKI JAKARTA",
    "DIY": "DI YOGYAKARTA",
    "YOGYAKARTA": "DI YOGYAKARTA",
    "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
    "KEPRI": "KEPULAUAN RIAU",
    "KEP RIAU": "KEPULAUAN RIAU",
    "KEP. RIAU": "KEPULAUAN RIAU",
    "BABEL": "BANGKA BELITUNG",
    "KEPULAUAN BANGKA BELITUNG": "BANGKA BELITUNG",
    "NTB": "NUSA TENGGARA BARAT (NTB)",
    "NUSA TENGGARA BARAT": "NUSA TENGGARA BARAT (NTB)",
    "NTT": "NUSA TENGGARA TIMUR (NTT)",
    "NUSA TENGGARA TIMUR": "NUSA TENGGARA TIMUR (NTT)",
    "KALTIM": "KALIMANTAN TIMUR",
    "KALSEL": "KALIMANTAN SELATAN",
    "KALBAR": "KALIMANTAN BARAT",
    "KALTENG": "KALIMANTAN TENGAH",
    "KALTARA": "KALIMANTAN UTARA",
    "SULSEL": "SULAWESI SELATAN",
    "SULBAR": "SULAWESI BARAT",
    "SULTENG": "SULAWESI TENGAH",
    "SULTRA": "SULAWESI TENGGARA",
    "SULUT": "SULAWESI UTARA",
    "SUMUT": "SUMATERA UTARA",
    "SUMBAR": "SUMATERA BARAT",
    "SUMSEL": "SUMATERA SELATAN",
    "JABAR": "JAWA BARAT",
    "JATENG": "JAWA TENGAH",
    "JATIM": "JAWA TIMUR",
}


def normalize_province(value):
    if pd.isna(value):
        return "UNKNOWN"

    text = str(value).upper().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = " ".join(text.split())

    if text in PROVINCE_ALIASES:
        return PROVINCE_ALIASES[text]

    if text in MASTER_PROVINCES:
        return text

    match = get_close_matches(text, MASTER_PROVINCES, n=1, cutoff=0.80)
    if match:
        return match[0]

    return text