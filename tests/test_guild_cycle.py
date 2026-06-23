"""
Tests unitaires pour le cycle Guildes → Fulus → CRD

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.guild_crd_cycle import GuildCRDCycle
from core.scaling_model import ScalingModel
from core.grondona_crd import GrondonaCRD


class TestScalingModel:
    """Tests pour les lois d'échelle"""

    def test_establishments(self):
        model = ScalingModel(eta=21.6, beta=0.92)
        n_f = model.establishments(1000)
        assert n_f == 21600  # 21.6 * 1000

    def test_diversity(self):
        model = ScalingModel(eta=21.6, beta=0.92)
        div = model.diversity(1000)
        assert div > 0
        assert div < 1000  # N^β < N pour β < 1

    def test_sector_diversity(self):
        model = ScalingModel(eta=21.6, beta=0.92)

        finance = model.sector_diversity(1000, 'finance')
        agriculture = model.sector_diversity(1000, 'agriculture')

        assert finance > agriculture  # Finance a β plus élevé

    def test_production_capacity(self):
        model = ScalingModel(eta=21.6, beta=0.92)
        metrics = model.compute_metrics(1000)

        assert metrics['production_capacity'] == metrics['establishments'] * metrics['diversity']

    def test_rank_abundance(self):
        model = ScalingModel(eta=21.6, beta=0.92)
        ranks = np.arange(1, 11)
        abundance = model.rank_abundance(ranks)

        assert len(abundance) == 10
        assert abundance[0] > abundance[-1]  # Décroissant


class TestGuildCRDCycle:
    """Tests pour le cycle vertueux"""

    def test_initialization(self):
        cycle = GuildCRDCycle()
        assert cycle.eta == 21.6
        assert cycle.beta == 0.92
        assert cycle.lambda_invest == 0.7
        assert cycle.kappa == 0.8
        assert cycle.rho == 0.5

    def test_single_step(self):
        cycle = GuildCRDCycle()
        result = cycle.step(N=1000)

        assert result.fulus_produced > 0
        assert result.invested == 0.7 * result.fulus_produced
        assert result.cbu_issued > 0
        assert result.reinvested == 0.5 * result.cbu_issued
        assert result.new_fulus > 0

    def test_simulation(self):
        cycle = GuildCRDCycle()
        results = cycle.run_simulation(N0=1000, n_steps=10)

        assert len(results) == 10
        assert results[0].period == 0
        assert results[-1].period == 9

    def test_summary(self):
        cycle = GuildCRDCycle()
        cycle.run_simulation(N0=1000, n_steps=10)
        summary = cycle.get_summary()

        assert 'n_periods' in summary
        assert summary['n_periods'] == 10
        assert 'total_fulus_produced' in summary
        assert 'total_cbu_issued' in summary
        assert summary['total_fulus_produced'] > 0
        assert summary['total_cbu_issued'] > 0

    def test_backing_ratio(self):
        cycle = GuildCRDCycle()
        cycle.run_simulation(N0=1000, n_steps=5)

        summary = cycle.get_summary()
        assert summary['average_backing_ratio'] > 0
        assert summary['final_backing_ratio'] > 0

    def test_population_growth(self):
        cycle = GuildCRDCycle()
        results = cycle.run_simulation(N0=1000, n_steps=20)

        # La population doit croître
        assert results[-1].population > results[0].population


class TestCRDInvestment:
    """Tests pour l'investissement dans le CRD"""

    def test_invest_fulus(self):
        crd = GrondonaCRD(coverage_rate=0.8)
        crd.add_commodity("blé", floor_price=80, ceiling_price=120,
                          initial_price=100, initial_stock=0)

        success = crd.invest_fulus("guild_1", 10000, "blé")
        assert success == True
        assert crd.cbu_supply > 0
        assert len(crd.investment_history) == 1

    def test_investment_return(self):
        crd = GrondonaCRD(coverage_rate=0.8)
        crd.add_commodity("blé", floor_price=80, ceiling_price=120,
                          initial_price=100, initial_stock=0)

        crd.invest_fulus("guild_1", 10000, "blé")

        # Augmenter le prix pour simuler une plus-value
        crd.commodities["blé"].current_price = 110

        ret = crd.get_investment_return("guild_1")
        assert ret > 0  # Plus-value positive

    def test_total_investments(self):
        crd = GrondonaCRD(coverage_rate=0.8)
        crd.add_commodity("blé", floor_price=80, ceiling_price=120,
                          initial_price=100, initial_stock=0)
        crd.add_commodity("or", floor_price=1600, ceiling_price=2200,
                          initial_price=1800, initial_stock=0)

        crd.invest_fulus("guild_1", 10000, "blé")
        crd.invest_fulus("guild_2", 20000, "or")

        totals = crd.get_total_investments()
        assert len(totals) == 2
        assert totals["blé"] > 0
        assert totals["or"] > 0

    def test_backing_ratio(self):
        crd = GrondonaCRD(coverage_rate=0.8)
        crd.add_commodity("blé", floor_price=80, ceiling_price=120,
                          initial_price=100, initial_stock=0)

        crd.invest_fulus("guild_1", 10000, "blé")

        ratio = crd.get_backing_ratio()
        assert ratio > 0
        # Avec 80% de couverture, le ratio devrait être > 1.0
        # car les stocks valent plus que les CBU émis
        assert ratio > 1.0
