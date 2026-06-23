"""
Tests unitaires pour les agents de simulation

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from simulation.agents import HouseholdAgent, FinancialAgent, MonetaryModel
from simulation.yusuf_model import YusufConfig, YusufSystem, CapitalistSystem


class TestHouseholdAgent:
    """Tests pour l'agent ménage"""

    def test_production(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]

        initial_wealth = agent.wealth
        output = agent.produce()

        assert output > 0
        assert agent.wealth > initial_wealth

    def test_consumption(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]

        initial_wealth = agent.wealth
        agent.produce()
        consumption = agent.consume_and_save()

        assert consumption > 0
        assert consumption <= initial_wealth + agent.production

    def test_zakat_payment(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]

        agent.wealth = 200  # Above nisab
        zakat = agent.pay_zakat(rate=0.025, nisab=100)

        assert zakat > 0
        assert agent.wealth == 200 - zakat

    def test_mudaraba(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]

        agent.wealth = 1000
        result = agent.mudaraba_invest(500, profit_share_ratio=0.7, risk_factor=0.0)

        assert result != 0


class TestMonetaryModel:
    """Tests pour le modèle monétaire"""

    def test_gini_computation(self):
        model = MonetaryModel(n_agents=100)
        gini = model.compute_gini()

        assert 0 <= gini <= 1

    def test_gdp_computation(self):
        model = MonetaryModel(n_agents=10)

        for _ in range(10):
            model.step()

        gdp = model.compute_gdp()
        assert gdp >= 0

    def test_default_rate(self):
        model = MonetaryModel(n_agents=10)

        for _ in range(50):
            model.step(shock_intensity=0.5)

        default_rate = model.compute_default_rate()
        assert 0 <= default_rate <= 1

    def test_run_simulation(self):
        model = MonetaryModel(n_agents=10)
        data = model.run_simulation(steps=20)

        assert len(data) == 20
        assert "GDP" in data.columns
        assert "Gini" in data.columns


class TestYusufModel:
    """Tests pour le modèle Yusuf"""

    def test_yusuf_vs_capitalist(self):
        config = YusufConfig(T=50, dt=0.5)

        yusuf = YusufSystem(config)
        capitalist = CapitalistSystem(config)

        y_res = yusuf.run()
        c_res = capitalist.run()

        assert y_res.solvency_rate >= c_res.solvency_rate
        assert y_res.consumption_volatility <= c_res.consumption_volatility

    def test_yusuf_solvency(self):
        config = YusufConfig(T=100, dt=0.5)
        yusuf = YusufSystem(config)
        res = yusuf.run()

        assert res.solvency_rate == 100.0

    def test_monte_carlo(self):
        config = YusufConfig(T=20, dt=1.0)
        comparator = YusufConfig()

        # Simple test that it runs without error
        yusuf = YusufSystem(config)
        res = yusuf.run()
        assert res.final_stock >= 0
