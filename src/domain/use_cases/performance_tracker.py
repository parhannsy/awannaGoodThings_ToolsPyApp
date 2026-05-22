"""
Use Case: PerformanceTrackerUseCase
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import uuid


@dataclass
class ProcessingRecord:
    """Record of a data processing operation."""
    
    id: str
    timestamp: datetime
    file_name: str
    file_size: int
    row_count: int
    processing_time_ms: float
    status: str
    error_message: Optional[str] = None
    output_path: Optional[Path] = None
    regions_processed: int = 0


class PerformanceTrackerUseCase:
    """Track and record processing performance."""
    
    def __init__(self):
        self._history: List[ProcessingRecord] = []
        self._current_start_time: Optional[float] = None
    
    def start_tracking(self) -> None:
        self._current_start_time = time.perf_counter()
    
    def stop_tracking(self) -> float:
        if self._current_start_time is None:
            return 0.0
        
        elapsed = (time.perf_counter() - self._current_start_time) * 1000
        self._current_start_time = None
        return elapsed
    
    def record_processing(
        self,
        file_path: Path,
        row_count: int,
        status: str,
        regions_processed: int = 0,
        output_path: Optional[Path] = None,
        error_message: Optional[str] = None
    ) -> ProcessingRecord:
        elapsed = self.stop_tracking()
        
        record = ProcessingRecord(
            id=self._generate_id(),
            timestamp=datetime.now(),
            file_name=file_path.name,
            file_size=file_path.stat().st_size if file_path.exists() else 0,
            row_count=row_count,
            processing_time_ms=elapsed,
            status=status,
            error_message=error_message,
            output_path=output_path,
            regions_processed=regions_processed
        )
        
        self._history.append(record)
        return record
    
    def get_history(self) -> List[ProcessingRecord]:
        return self._history.copy()
    
    def get_latest(self, count: int = 10) -> List[ProcessingRecord]:
        return self._history[-count:][::-1]
    
    def get_average_processing_time(self) -> float:
        if not self._history:
            return 0.0
        return sum(r.processing_time_ms for r in self._history) / len(self._history)
    
    def _generate_id(self) -> str:
        return str(uuid.uuid4())[:8]