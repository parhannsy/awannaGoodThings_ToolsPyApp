"""
DTO: SummaryResponse
"""

from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

from domain.entities.sales_summary import RegionalSummary


@dataclass
class SummaryResponse:
    """Response containing regional summary results."""
    
    success: bool
    message: str
    summaries: List[RegionalSummary]
    statistics: Dict
    output_path: Path = None
    processing_time_ms: float = 0.0
    error_details: str = None