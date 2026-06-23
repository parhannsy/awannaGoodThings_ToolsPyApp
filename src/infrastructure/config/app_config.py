"""
Configuration: AppConfig
Konfigurasi aplikasi, constants, dan manajemen penyimpanan persistent lokal.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration with cache persistence capabilities."""
    
    APP_NAME: str = "Awanna media's Tools"
    APP_VERSION: str = "1.1.0"
    APP_WIDTH: int = 1200
    APP_HEIGHT: int = 800
    
    # Default directories
    OUTPUT_DIR: Path = Path.home() / "Documents" / "SalesTool_Output"
    
    # 🌟 PERBAIKAN: Definisikan basis direktori cache internal aplikasi
    CACHE_DIR: Path = Path("data/cache")
    
    # File filters for dialog
    FILE_TYPES = [
        ("Excel files", "*.xlsx *.xls"),
        ("CSV files", "*.csv"),
        ("All files", "*.*")
    ]
    
    # Theme
    THEME: str = "dark"  # "dark" or "light"
    COLOR_THEME: str = "blue"  # "blue", "green", "dark-blue"
    
    def ensure_directories(self):
        """Create necessary directories."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # 🌟 PERBAIKAN: Pastikan folder cache internal juga ikut dibuat saat aplikasi di-run
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get_last_login_email(self) -> str:
        """Membaca email terakhir yang sukses login dari penyimpanan lokal."""
        try:
            cache_file = self.CACHE_DIR / ".last_login"
            if cache_file.exists():
                return cache_file.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"[CONFIG ERROR] Gagal membaca email terakhir: {e}")
        return ""

    def save_last_login_email(self, email: str):
        """Menyimpan email yang sukses login ke penyimpanan lokal."""
        try:
            cache_file = self.CACHE_DIR / ".last_login"
            cache_file.write_text(email.strip(), encoding="utf-8")
            print(f"[CONFIG] Email '{email}' berhasil disimpan lokal untuk login berikutnya.")
        except Exception as e:
            print(f"[CONFIG ERROR] Gagal menyimpan email terakhir: {e}")