"""
Tests unitaires pour l'entropie

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.entropy_physical import PhysicalEntropy
from core.entropy_shannon import ShannonEntropy


class TestPhysicalEntropy:
    """Tests pour l'entropie physique"""

    def test_production_entropy_positive(self):
        entropy = PhysicalEntropy()
        result = entropy.production_entropy(10)
        assert result > 0

    def test_negentropy_capture(self):
        entropy = PhysicalEntropy()
        result = entropy.negentropy_capture(5, gamma=0.8)
        assert result == 4.0

    def test_critical_interest_rate(self):
        entropy = PhysicalEntropy()
        rate = entropy.find_critical_interest_rate(
            debt=100, low_entropy_extraction=10
        )
        assert 0 < rate < 0.1

        # Verify at critical rate, lambda ≈ 1
        lambda_val = entropy.bifurcation_parameter(100, rate, 10)
        assert abs(lambda_val - 1.0) < 0.001


class TestShannonEntropy:
    """Tests pour l'entropie de Shannon"""

    def test_price_entropy_uniform(self):
        prices = [10, 10, 10, 10]
        entropy = ShannonEntropy.price_entropy(prices)
        assert entropy >= 0

    def test_price_entropy_diverse(self):
        prices = [10, 20, 30, 40, 50]
        entropy = ShannonEntropy.price_entropy(prices)
        assert entropy > 0

    def test_transaction_entropy(self):
        transactions = [100, 200, 300, 400]
        entropy = ShannonEntropy.transaction_entropy(transactions)
        assert entropy > 0

    def test_empty_list(self):
        assert ShannonEntropy.price_entropy([]) == 0.0
        assert ShannonEntropy.transaction_entropy([]) == 0.0
