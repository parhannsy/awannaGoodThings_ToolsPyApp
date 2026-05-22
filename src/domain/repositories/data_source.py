"""
Repository Interface: DataSourceRepository
Abstract interface untuk sumber data (Excel/CSV).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from ..entities.transaction import Transaction


class DataSourceRepository(ABC):
    """Abstract repository for reading sales data from files."""
    
    @abstractmethod
    def read_transactions(self, file_path: Path) -> List[Transaction]:
        """
        Read and parse transactions from a file.
        
        Args:
            file_path: Path to Excel or CSV file
            
        Returns:
            List of Transaction entities
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass
    
    @abstractmethod
    def validate_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate if file is readable and has required columns.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: Path) -> dict:
        """Get metadata about the file (size, row count, etc.)."""
        pass