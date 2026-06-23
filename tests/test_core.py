"""
Tests unitaires pour les modules core

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.grondona_crd import GrondonaCRD, simulate_crd
from core.entropy_physical import PhysicalEntropy, detect_chrematistic_absurdity
from core.nuqud import NuqudReserve
from core.fulus import FulusSystem
from core.hisba import HisbaInstitution
from core.zakat_nuqud import ZakatSystem


class TestGrondonaCRD:
    """Tests pour le CRD"""

    def test_crd_initialization(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)

        assert len(crd.commodities) == 1
        assert crd.commodities["Test"].stock == 100
        assert crd.commodities["Test"].floor_price == 100
        assert crd.commodities["Test"].ceiling_price == 200

    def test_crd_buy_action(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)

        actions = crd.step({"Test": 80})

        assert actions["Test"]["action"] == "buy"
        assert actions["Test"]["quantity"] > 0
        assert crd.money_supply > 0

    def test_crd_sell_action(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)

        actions = crd.step({"Test": 250})

        assert actions["Test"]["action"] == "sell"
        assert actions["Test"]["quantity"] > 0

    def test_crd_simulation(self):
        initial_prices = {"Blé": 200, "Cuivre": 10000, "Coton": 80}
        results = simulate_crd(initial_prices, periods=50)

        assert len(results) == 50
        assert results[0]["money_supply"] >= 0
        assert results[-1]["money_supply"] >= 0


class TestEntropy:
    """Tests pour l'entropie physique"""

    def test_bifurcation_stable(self):
        entropy = PhysicalEntropy()

        lambda_val = entropy.bifurcation_parameter(
            debt=100, interest_rate=0.03, low_entropy_extraction=10
        )
        assert lambda_val < 1.0

    def test_bifurcation_unstable(self):
        entropy = PhysicalEntropy()

        lambda_val = entropy.bifurcation_parameter(
            debt=100, interest_rate=0.03, low_entropy_extraction=1
        )
        assert lambda_val > 1.0

    def test_collapse_detection(self):
        entropy = PhysicalEntropy()

        t, collapsed = entropy.collapse_threshold(
            initial_debt=1000, interest_rate=0.05, low_entropy_extraction=10
        )
        assert collapsed == True
        assert t < 100

    def test_negative_price_detection(self):
        assert detect_chrematistic_absurdity(-37.63, 7.2) is True
        assert detect_chrematistic_absurdity(70.0, 7.2) is False

    def test_total_entropy(self):
        entropy = PhysicalEntropy()
        result = entropy.total_entropy(
            initial_entropy=0.5,
            production_quantities=[10, 12, 8],
            stock_variations=[5, -2, 3]
        )
        assert len(result) == 4
        assert all(r >= 0 for r in result)


class TestNuqud:
    """Tests pour les nuqud"""

    def test_nuqud_value(self):
        reserve = NuqudReserve(gold_grams=100, silver_grams=500)
        value = reserve.total_value_usd()
        expected = 100 * 55.0 + 500 * 0.75
        assert value == expected

    def test_nuqud_withdrawal(self):
        reserve = NuqudReserve(gold_grams=100, silver_grams=500)

        assert reserve.withdraw_gold(50) == True
        assert reserve.gold_grams == 50

        assert reserve.withdraw_gold(100) == False
        assert reserve.gold_grams == 50


class TestFulus:
    """Tests pour les fulus"""

    def test_fulus_creation(self):
        system = FulusSystem()
        wallet = system.create_wallet("addr1", 1000)
        assert wallet.balance == 1000
        assert system.total_supply == 1000

    def test_fulus_transfer(self):
        system = FulusSystem()
        system.create_wallet("addr1", 1000)
        system.create_wallet("addr2", 0)

        result = system.transfer("addr1", "addr2", 500)
        assert result == True
        assert system.wallets["addr1"].balance == 500
        assert system.wallets["addr2"].balance == 500

    def test_fulus_demurrage(self):
        system = FulusSystem(demurrage_rate=0.025)
        system.create_wallet("addr1", 1000)

        decay = system.apply_demurrage("addr1")
        assert decay > 0
        assert system.wallets["addr1"].balance < 1000


class TestHisba:
    """Tests pour l'inspection du marché"""

    def test_weight_inspection(self):
        hisba = HisbaInstitution()
        result = hisba.inspect_weights_and_measures("wheat", 100, 100.5)
        assert result == True

        result = hisba.inspect_weights_and_measures("wheat", 100, 95)
        assert result == False
        assert len(hisba.violations) == 1

    def test_price_manipulation(self):
        hisba = HisbaInstitution()
        prices = {"wheat": 300}
        historical = {"wheat": [200, 210, 205, 215, 220] * 10}

        violations = hisba.detect_market_manipulation(prices, historical)
        assert len(violations) > 0


class TestZakat:
    """Tests pour la Zakat"""

    def test_zakat_computation(self):
        zakat = ZakatSystem()
        gold_zakat, silver_zakat = zakat.compute_zakat(
            gold_grams=100, silver_grams=500,
            cash_equivalent=1000, trade_goods_value=500
        )
        assert gold_zakat > 0 or silver_zakat > 0

    def test_zakat_collection(self):
        zakat = ZakatSystem()
        result = zakat.collect_zakat(gold_grams=100, silver_grams=500, payer_id="payer1")

        assert result["success"] == True
        assert zakat.total_collected_gold > 0 or zakat.total_collected_silver > 0

    def test_zakat_report(self):
        zakat = ZakatSystem()
        zakat.collect_zakat(gold_grams=100, silver_grams=500, payer_id="payer1")
        report = zakat.get_report()

        assert report["total_collected_gold"] > 0
        assert report["history_count"] == 1
