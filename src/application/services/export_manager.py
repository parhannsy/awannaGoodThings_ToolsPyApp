"""
Service: ExportManagerService
"""

from pathlib import Path
from typing import List

from domain.entities.sales_summary import RegionalSummary
from infrastructure.persistence.excel_writter import ExcelWriter


class ExportManagerService:
    """Manage export operations to Excel."""
    
    def __init__(self, excel_writer: ExcelWriter):
        self._writer = excel_writer
    
    def export_regional_summary(
        self,
        summaries: List[RegionalSummary],
        output_path: Path,
        include_details: bool = False
    ) -> Path:
        return self._writer.write_regional_summary(
            summaries=summaries,
            output_path=output_path,
            include_details=include_details
        )
    
    def export_full_report(
        self,
        summaries: List[RegionalSummary],
        statistics: dict,
        output_path: Path
    ) -> Path:
        return self._writer.write_full_report(
            summaries=summaries,
            statistics=statistics,
            output_path=output_path
        )