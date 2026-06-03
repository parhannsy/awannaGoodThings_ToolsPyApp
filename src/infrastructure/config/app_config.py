"""
Configuration: AppConfig
Konfigurasi aplikasi dan constants.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration."""
    
    APP_NAME: str = "Awanna media's Tools"
    APP_VERSION: str = "1.0.0"
    APP_WIDTH: int = 1200
    APP_HEIGHT: int = 800
    
    # Default directories
    OUTPUT_DIR: Path = Path.home() / "Documents" / "SalesTool_Output"
    
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