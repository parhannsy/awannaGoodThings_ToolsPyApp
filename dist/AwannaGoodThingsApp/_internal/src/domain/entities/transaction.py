"""
Entity: Transaction
Representasi domain dari satu transaksi penjualan.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Domain entity representing a sales transaction."""
    
    transaction_id: str
    date: datetime
    product_name: str
    region: str
    payment_status: str  # "paid", "pending", "cancelled", etc.
    amount: Optional[float] = None
    quantity: Optional[int] = None
    
    def is_paid(self) -> bool:
        """Check if transaction status is paid."""
        return self.payment_status.lower() == "paid"
    
    def __post_init__(self):
        """Validate entity after creation."""
        if not self.transaction_id:
            raise ValueError("Transaction ID cannot be empty")
        if not self.region:
            raise ValueError("Region cannot be empty")