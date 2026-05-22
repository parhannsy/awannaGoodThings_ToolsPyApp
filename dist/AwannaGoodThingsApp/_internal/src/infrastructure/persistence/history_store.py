"""
Adapter: HistoryStore
"""

import json
from pathlib import Path
from typing import List
from datetime import datetime

from domain.use_cases.performance_tracker import ProcessingRecord


class HistoryStore:
    """Store processing history to local file."""
    
    def __init__(self, storage_path: Path = None):
        if storage_path is None:
            app_dir = Path.home() / ".sales_data_tool"
            app_dir.mkdir(exist_ok=True)
            storage_path = app_dir / "history.json"
        
        self._storage_path = storage_path
        self._records: List[ProcessingRecord] = []
        self._load()
    
    def save_record(self, record: ProcessingRecord) -> None:
        self._records.append(record)
        self._persist()
    
    def get_all_records(self) -> List[ProcessingRecord]:
        return self._records.copy()
    
    def get_recent_records(self, count: int = 10) -> List[ProcessingRecord]:
        return self._records[-count:][::-1]
    
    def clear_history(self) -> None:
        self._records = []
        self._persist()
    
    def _persist(self) -> None:
        data = [self._record_to_dict(r) for r in self._records]
        with open(self._storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self) -> None:
        if not self._storage_path.exists():
            return
        
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._records = [self._dict_to_record(d) for d in data]
        except (json.JSONDecodeError, KeyError):
            self._records = []
    
    def _record_to_dict(self, record: ProcessingRecord) -> dict:
        return {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "file_name": record.file_name,
            "file_size": record.file_size,
            "row_count": record.row_count,
            "processing_time_ms": record.processing_time_ms,
            "status": record.status,
            "error_message": record.error_message,
            "output_path": str(record.output_path) if record.output_path else None,
            "regions_processed": record.regions_processed
        }
    
    def _dict_to_record(self, data: dict) -> ProcessingRecord:
        return ProcessingRecord(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            file_name=data["file_name"],
            file_size=data["file_size"],
            row_count=data["row_count"],
            processing_time_ms=data["processing_time_ms"],
            status=data["status"],
            error_message=data.get("error_message"),
            output_path=Path(data["output_path"]) if data.get("output_path") else None,
            regions_processed=data.get("regions_processed", 0)
        )