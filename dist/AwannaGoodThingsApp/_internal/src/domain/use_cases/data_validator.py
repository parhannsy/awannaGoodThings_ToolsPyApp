"""
Use Case: DataValidatorUseCase
"""

from typing import List, Tuple
from pathlib import Path

from domain.repositories.data_source import DataSourceRepository
from domain.entities.transaction import Transaction


class DataValidatorUseCase:
    """Validate incoming data before processing."""
    
    REQUIRED_COLUMNS = ["tanggal", "nama_produk", "wilayah", "status_pembayaran"]
    
    def __init__(self, data_source: DataSourceRepository):
        self._data_source = data_source
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        errors = []
        
        if not file_path.exists():
            return False, [f"File tidak ditemukan: {file_path}"]
        
        valid_extensions = {'.xlsx', '.xls', '.csv'}
        if file_path.suffix.lower() not in valid_extensions:
            errors.append(f"Format file tidak didukung: {file_path.suffix}")
            return False, errors
        
        is_valid, error_msg = self._data_source.validate_file(file_path)
        if not is_valid:
            errors.append(error_msg or "Validasi file gagal")
        
        return len(errors) == 0, errors
    
    def validate_transactions(self, transactions: List[Transaction]) -> Tuple[bool, List[str]]:
        errors = []
        
        if not transactions:
            errors.append("Tidak ada data transaksi yang ditemukan")
            return False, errors
        
        empty_regions = [t for t in transactions if not t.region.strip()]
        if empty_regions:
            errors.append(f"Ditemukan {len(empty_regions)} transaksi tanpa wilayah")
        
        return len(errors) == 0, errors