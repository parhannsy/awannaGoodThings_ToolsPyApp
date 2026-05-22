"""
Tests for domain entities.
"""

import pytest
from datetime import datetime
from src.domain.entities.transaction import Transaction
from src.domain.entities.sales_summary import RegionalSummary


class TestTransaction:
    """Test Transaction entity."""
    
    def test_create_valid_transaction(self):
        txn = Transaction(
            transaction_id="TXN-001",
            date=datetime.now(),
            product_name="Laptop",
            region="JAKARTA",
            payment_status="paid",
            amount=1000000.0,
            quantity=1
        )
        assert txn.is_paid() is True
    
    def test_unpaid_transaction(self):
        txn = Transaction(
            transaction_id="TXN-002",
            date=datetime.now(),
            product_name="Mouse",
            region="BANDUNG",
            payment_status="pending"
        )
        assert txn.is_paid() is False
    
    def test_invalid_transaction(self):
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="",
                date=datetime.now(),
                product_name="Test",
                region="",
                payment_status="paid"
            )


class TestRegionalSummary:
    """Test RegionalSummary entity."""
    
    def test_empty_summary(self):
        summary = RegionalSummary(region="JAKARTA")
        assert summary.total_transactions == 0
        assert summary.payment_rate == 0.0
    
    def test_add_transactions(self):
        summary = RegionalSummary(region="SURABAYA")
        
        txn1 = Transaction("TXN-001", datetime.now(), "A", "SURABAYA", "paid", 1000)
        txn2 = Transaction("TXN-002", datetime.now(), "B", "SURABAYA", "pending", 500)
        
        summary.add_transaction(txn1)
        summary.add_transaction(txn2)
        
        assert summary.total_transactions == 2
        assert summary.paid_transactions == 1
        assert summary.payment_rate == 0.5
        assert summary.payment_percentage == 50.0