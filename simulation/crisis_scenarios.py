"""
Module de scénarios de crise
Test des réponses du système Grondona

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple
from core.grondona_crd import GrondonaCRD


def simulate_invasion_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: invasion bloquant les routes commerciales"""
    crd = GrondonaCRD()
    crd.add_commodity('wheat', floor_price=180, ceiling_price=220, 
                      initial_price=200, initial_stock=1000)
    crd.add_commodity('copper', floor_price=8000, ceiling_price=12000,
                      initial_price=10000, initial_stock=500)
    crd.add_commodity('oil', floor_price=70, ceiling_price=90,
                      initial_price=80, initial_stock=2000)

    results = []
    for period in range(periods):
        market_prices = {}

        for name, c in crd.commodities.items():
            if period < 100:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                if name == 'wheat':
                    shock = 1 + np.random.normal(0.3, 0.1)
                elif name == 'oil':
                    shock = 1 + np.random.normal(0.5, 0.15)
                else:
                    shock = 1 + np.random.normal(0.1, 0.05)

            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])

        actions = crd.step(market_prices)

        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value(),
            'prices': {name: c.current_price for name, c in crd.commodities.items()},
            'stocks': {name: c.stock for name, c in crd.commodities.items()}
        })

    return results


def simulate_famine_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: famine causant une chute de la production"""
    crd = GrondonaCRD()
    crd.add_commodity('wheat', floor_price=180, ceiling_price=220,
                      initial_price=200, initial_stock=2000)
    crd.add_commodity('rice', floor_price=160, ceiling_price=200,
                      initial_price=180, initial_stock=1500)

    results = []
    for period in range(periods):
        market_prices = {}

        for name, c in crd.commodities.items():
            if period < 80:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                shock = 1 + np.random.normal(0.4, 0.1)

            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])

        actions = crd.step(market_prices)

        for name, c in crd.commodities.items():
            consumption = c.stock * 0.01
            c.stock -= consumption

        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value()
        })

    return results


def simulate_panic_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: panique bancaire menant à une ruée sur les dépôts"""
    crd = GrondonaCRD()
    crd.add_commodity('gold', floor_price=1800, ceiling_price=2200,
                      initial_price=2000, initial_stock=100)
    crd.add_commodity('silver', floor_price=25, ceiling_price=30,
                      initial_price=27, initial_stock=500)

    results = []
    panic_started = False

    for period in range(periods):
        market_prices = {}

        for name, c in crd.commodities.items():
            if period < 100:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                if not panic_started:
                    shock = 0.7
                    panic_started = True
                else:
                    shock = 0.9 + 0.1 * (period - 100) / 100

            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])

        actions = crd.step(market_prices)

        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value()
        })

    return results
