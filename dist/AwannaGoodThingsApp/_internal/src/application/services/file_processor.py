"""
Service: FileProcessorService
"""

from pathlib import Path
from typing import Tuple, List

from domain.repositories.data_source import DataSourceRepository
from domain.use_cases.data_validator import DataValidatorUseCase
from domain.use_cases.regional_aggregator import RegionalAggregatorUseCase
from domain.use_cases.performance_tracker import PerformanceTrackerUseCase
from domain.entities.sales_summary import RegionalSummary
from application.dto.file_request import FileRequest
from application.dto.summary_response import SummaryResponse


class FileProcessorService:
    """Orchestrate file processing workflow."""
    
    def __init__(
        self,
        data_source: DataSourceRepository,
        validator: DataValidatorUseCase,
        aggregator: RegionalAggregatorUseCase,
        tracker: PerformanceTrackerUseCase
    ):
        self._data_source = data_source
        self._validator = validator
        self._aggregator = aggregator
        self._tracker = tracker
    
    def process_file(self, request: FileRequest) -> SummaryResponse:
        self._tracker.start_tracking()
        
        is_valid, errors = self._validator.validate_file(request.file_path)
        if not is_valid:
            record = self._tracker.record_processing(
                file_path=request.file_path,
                row_count=0,
                status="failed",
                error_message="; ".join(errors)
            )
            return SummaryResponse(
                success=False,
                message="Validasi gagal",
                summaries=[],
                statistics={},
                error_details="; ".join(errors),
                processing_time_ms=record.processing_time_ms
            )
        
        try:
            summaries = self._aggregator.aggregate_by_region(request.file_path)
            stats = self._aggregator.get_summary_statistics(summaries)
            
            record = self._tracker.record_processing(
                file_path=request.file_path,
                row_count=stats["total_transactions"],
                status="success",
                regions_processed=stats["total_regions"],
                output_path=request.get_output_path()
            )
            
            return SummaryResponse(
                success=True,
                message=f"Berhasil memproses {stats['total_transactions']} transaksi",
                summaries=summaries,
                statistics=stats,
                output_path=request.get_output_path(),
                processing_time_ms=record.processing_time_ms
            )
            
        except Exception as e:
            record = self._tracker.record_processing(
                file_path=request.file_path,
                row_count=0,
                status="failed",
                error_message=str(e)
            )
            return SummaryResponse(
                success=False,
                message="Proses agregasi gagal",
                summaries=[],
                statistics={},
                error_details=str(e),
                processing_time_ms=record.processing_time_ms
            )