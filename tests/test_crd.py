"""
Tests unitaires avancés pour le CRD

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.grondona_crd import GrondonaCRD, simulate_crd


class TestCRDAdvanced:
    """Tests avancés pour le CRD"""

    def test_entropy_bound(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=100)
        crd.add_commodity("B", floor_price=5, ceiling_price=15, initial_price=10, initial_stock=200)

        entropy = crd.get_entropy_bound()
        assert entropy >= 0

    def test_total_stock_value(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=100)

        value = crd.total_stock_value()
        assert value == 1500  # 100 * 15

    def test_money_supply_never_negative(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=1000)

        for _ in range(100):
            price = 15 + np.random.normal(0, 5)
            price = max(1, price)
            crd.step({"A": price})

        assert crd.money_supply >= 0

    def test_simulation_stability(self):
        initial_prices = {"A": 100, "B": 50, "C": 25}
        results = simulate_crd(initial_prices, periods=200, price_volatility=0.3)

        money_supplies = [r["money_supply"] for r in results]
        assert all(m >= 0 for m in money_supplies)
