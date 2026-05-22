"""
Use Case: RegionalAggregatorUseCase
"""

from typing import List, Dict
from pathlib import Path
from collections import defaultdict

from domain.repositories.data_source import DataSourceRepository
from domain.entities.transaction import Transaction
from domain.entities.sales_summary import RegionalSummary


class RegionalAggregatorUseCase:
    """Aggregate transactions by region with payment status analysis."""
    
    def __init__(self, data_source: DataSourceRepository):
        self._data_source = data_source
    
    def aggregate_by_region(self, file_path: Path) -> List[RegionalSummary]:
        transactions = self._data_source.read_transactions(file_path)
        return self._aggregate(transactions)
    
    def _aggregate(self, transactions: List[Transaction]) -> List[RegionalSummary]:
        region_groups: Dict[str, RegionalSummary] = {}
        
        for transaction in transactions:
            region = transaction.region.strip().upper()
            
            if region not in region_groups:
                region_groups[region] = RegionalSummary(region=region)
            
            region_groups[region].add_transaction(transaction)
        
        return sorted(
            region_groups.values(),
            key=lambda x: x.total_transactions,
            reverse=True
        )
    
    def get_summary_statistics(self, summaries: List[RegionalSummary]) -> dict:
        total_all = sum(s.total_transactions for s in summaries)
        total_paid = sum(s.paid_transactions for s in summaries)
        total_amount = sum(s.total_amount for s in summaries)
        
        return {
            "total_regions": len(summaries),
            "total_transactions": total_all,
            "total_paid": total_paid,
            "total_pending": total_all - total_paid,
            "overall_payment_rate": (total_paid / total_all * 100) if total_all > 0 else 0,
            "total_amount": total_amount,
            "top_region": summaries[0].region if summaries else None
        }