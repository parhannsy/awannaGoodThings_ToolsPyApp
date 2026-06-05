"""
Konstanta dan konfigurasi styling untuk Rate Zonasi.
"""

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

STATUS_DELIVE = {
    "dicairkan",
    "terkirim"
}

STATUS_RTS = {
    "dikembalikan"
}

COLORS = {
    "primary": "#3B82F6",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "bg_light": ("gray95", "gray10"),
    "bg_card": ("gray90", "gray17"),
    "bg_table": ("gray98", "gray13"),
    "text": ("gray10", "gray90"),
    "text_muted": ("gray50", "gray60"),
    "border": ("gray80", "gray30"),
}

FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 12),
    "header": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
}