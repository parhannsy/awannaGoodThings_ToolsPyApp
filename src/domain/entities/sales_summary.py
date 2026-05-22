"""
Entity: RegionalSummary
Ringkasan agregasi transaksi per wilayah.
"""

from dataclasses import dataclass, field
from typing import List
from .transaction import Transaction


@dataclass
class RegionalSummary:
    """Summary of transactions grouped by region."""
    
    region: str
    total_transactions: int = 0
    paid_transactions: int = 0
    pending_transactions: int = 0
    total_amount: float = 0.0
    paid_amount: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    
    @property
    def payment_rate(self) -> float:
        """Calculate payment completion rate (0.0 - 1.0)."""
        if self.total_transactions == 0:
            return 0.0
        return self.paid_transactions / self.total_transactions
    
    @property
    def payment_percentage(self) -> float:
        """Calculate payment completion percentage."""
        return self.payment_rate * 100
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to this regional summary."""
        self.transactions.append(transaction)
        self.total_transactions += 1
        self.total_amount += transaction.amount or 0
        
        if transaction.is_paid():
            self.paid_transactions += 1
            self.paid_amount += transaction.amount or 0
        else:
            self.pending_transactions += 1