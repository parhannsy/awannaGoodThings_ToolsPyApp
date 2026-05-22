"""
Adapter: ExcelReader
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from domain.repositories.data_source import DataSourceRepository
from domain.entities.transaction import Transaction


class ExcelReader(DataSourceRepository):
    """Read transactions from Excel or CSV files."""
    
    COLUMN_MAPPINGS = {
        "tanggal": ["tanggal", "date", "tgl", "tanggal_transaksi"],
        "nama_produk": ["nama_produk", "produk", "product_name", "item"],
        "wilayah": ["wilayah", "region", "area", "lokasi", "kota"],
        "status_pembayaran": ["status_pembayaran", "status", "payment_status", "paid"],
        "jumlah": ["jumlah", "amount", "total", "harga", "price"],
        "kuantitas": ["kuantitas", "qty", "quantity"]
    }
    
    def read_transactions(self, file_path: Path) -> List[Transaction]:
        df = self._read_dataframe(file_path)
        column_map = self._detect_columns(df)
        
        transactions = []
        for idx, row in df.iterrows():
            transaction = self._parse_row(row, column_map, idx)
            transactions.append(transaction)
        
        return transactions
    
    def validate_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        try:
            df = self._read_dataframe(file_path)
            
            if df.empty:
                return False, "File tidak memiliki data"
            
            column_map = self._detect_columns(df)
            missing = [k for k, v in column_map.items() if v is None]
            
            required = ["tanggal", "wilayah", "status_pembayaran"]
            missing_required = [c for c in required if c in missing]
            
            if missing_required:
                return False, f"Kolom wajib tidak ditemukan: {', '.join(missing_required)}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error membaca file: {str(e)}"
    
    def get_file_info(self, file_path: Path) -> dict:
        stat = file_path.stat()
        df = self._read_dataframe(file_path)
        
        return {
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }
    
    def _read_dataframe(self, file_path: Path) -> pd.DataFrame:
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return pd.read_csv(file_path)
        elif suffix in {'.xlsx', '.xls'}:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Format tidak didukung: {suffix}")
    
    def _detect_columns(self, df: pd.DataFrame) -> dict:
        df_columns = [c.lower().strip() for c in df.columns]
        detected = {}
        
        for standard_name, aliases in self.COLUMN_MAPPINGS.items():
            found = None
            for alias in aliases:
                if alias.lower() in df_columns:
                    idx = df_columns.index(alias.lower())
                    found = df.columns[idx]
                    break
            
            detected[standard_name] = found
        
        return detected
    
    def _parse_row(self, row: pd.Series, column_map: dict, index: int) -> Transaction:
        date_val = row.get(column_map.get("tanggal"), datetime.now())
        if isinstance(date_val, str):
            date_val = pd.to_datetime(date_val)
        
        region_val = str(row.get(column_map.get("wilayah"), ""))
        status_val = str(row.get(column_map.get("status_pembayaran"), "unknown"))
        product_val = str(row.get(column_map.get("nama_produk"), "Unknown Product"))
        
        amount_val = row.get(column_map.get("jumlah"))
        if pd.isna(amount_val):
            amount_val = None
        else:
            amount_val = float(amount_val)
        
        qty_val = row.get(column_map.get("kuantitas"))
        if pd.isna(qty_val):
            qty_val = None
        else:
            qty_val = int(qty_val)
        
        return Transaction(
            transaction_id=f"TXN-{index:06d}",
            date=date_val if isinstance(date_val, datetime) else datetime.now(),
            product_name=product_val,
            region=region_val,
            payment_status=status_val,
            amount=amount_val,
            quantity=qty_val
        )