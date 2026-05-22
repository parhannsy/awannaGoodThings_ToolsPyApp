"""
DTO: FileRequest
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileRequest:
    """Request to process a data file."""
    
    file_path: Path
    output_directory: Path
    output_file_name: Optional[str] = None
    
    def get_output_path(self) -> Path:
        """Generate output file path."""
        name = self.output_file_name or f"processed_{self.file_path.stem}"
        return self.output_directory / f"{name}.xlsx"