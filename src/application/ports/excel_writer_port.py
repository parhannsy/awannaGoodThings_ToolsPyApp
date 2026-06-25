"""
Port: ExcelWriterPort
Abstract port for saving report data to Excel.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from domain.entities.sales_summary import RegionalSummary


class ExcelWriterPort(ABC):
    @abstractmethod
    def write_regional_summary(
        self,
        summaries: List[RegionalSummary],
        output_path: Path,
        include_details: bool = False
    ) -> Path:
        pass

    @abstractmethod
    def write_full_report(
        self,
        summaries: List[RegionalSummary],
        statistics: dict,
        output_path: Path
    ) -> Path:
        pass
