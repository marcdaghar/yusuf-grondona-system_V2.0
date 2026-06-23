"""
Script principal pour exécuter une simulation complète

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from core.grondona_crd import GrondonaCRD
from core.entropy_physical import PhysicalEntropy
from simulation.agents import MonetaryModel
from simulation.stress_test import run_stress_test, compare_regimes
from simulation.crisis_scenarios import (
    simulate_invasion_scenario,
    simulate_famine_scenario,
    simulate_panic_scenario
)


def main():
    print("=" * 60)
    print("SYSTÈME YUSUF-GRONDONA - SIMULATION COMPLÈTE")
    print("=" * 60)
    print()

    # 1. Simulation du CRD
    print("[1] Simulation du système Grondona")
    crd = GrondonaCRD()
    crd.add_commodity("Blé", floor_price=180, ceiling_price=220, 
                      initial_price=200, initial_stock=1000)
    crd.add_commodity("Cuivre", floor_price=8000, ceiling_price=12000,
                      initial_price=10000, initial_stock=500)
    crd.add_commodity("Coton", floor_price=70, ceiling_price=90,
                      initial_price=80, initial_stock=800)

    for period in range(200):
        market_prices = {}
        for name, c in crd.commodities.items():
            shock = 1 + np.random.normal(0, 0.1)
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])

        crd.step(market_prices)

    print(f"  Masse monétaire: {crd.money_supply:.0f}")
    print(f"  Valeur des stocks: {crd.total_stock_value():.0f}")
    print()

    # 2. Test de résistance
    print("[2] Test de résistance des régimes")
    df_comparison = compare_regimes()
    print(df_comparison.to_string(index=False))
    print()

    # 3. Scénarios de crise
    print("[3] Scénarios de crise")
    invasion_results = simulate_invasion_scenario(100)
    print(f"  Invasion - Masse finale: {invasion_results[-1]['money_supply']:.0f}")

    famine_results = simulate_famine_scenario(100)
    print(f"  Famine - Masse finale: {famine_results[-1]['money_supply']:.0f}")

    panic_results = simulate_panic_scenario(100)
    print(f"  Panique - Masse finale: {panic_results[-1]['money_supply']:.0f}")
    print()

    # 4. Paramètre de bifurcation
    print("[4] Paramètre de bifurcation Λ")
    entropy = PhysicalEntropy()

    debt = 1000
    interest_rate = 0.05
    low_entropy = 50

    lambda_val = entropy.bifurcation_parameter(debt, interest_rate, low_entropy)
    print(f"  Λ = {lambda_val:.3f}")
    print(f"  Statut: {'⚠️ COLLAPSOLOGIE' if lambda_val > 1 else '✅ STABLE'}")
    print()

    # 5. Détection d'absurdités
    print("[5] Détection d'absurdités chrématistiques")
    from core.entropy_physical import detect_chrematistic_absurdity

    wti_negative_price = -37.63
    energy_value = 7.2

    is_absurd = detect_chrematistic_absurdity(wti_negative_price, energy_value)
    print(f"  Prix WTI négatif (-37.63$) : {'⚠️ ABSURDE' if is_absurd else 'Normal'}")
    print()

    print("=" * 60)
    print("SIMULATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()
