"""
Script principal pour exécuter une simulation complète
Intègre le mécanisme purifié: Guildes → Fulus → CRD → CBU

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from core.grondona_crd import GrondonaCRD
from core.entropy_physical import PhysicalEntropy
from core.guild_crd_cycle import GuildCRDCycle, demonstrate_cycle
from core.scaling_model import ScalingModel
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
    print("Mécanisme purifié: Guildes → Fulus → CRD → CBU")
    print("=" * 60)
    print()

    # 1. Démonstration du cycle vertueux
    print("[1] Démonstration du Cycle Vertueux Guildes → Fulus → CRD")
    print("-" * 60)
    cycle = demonstrate_cycle()
    print()

    # 2. Simulation du CRD avec investissement des guildes
    print("[2] Simulation du CRD avec investissement des guildes")
    print("-" * 60)
    crd = GrondonaCRD(coverage_rate=0.8)
    crd.add_commodity("Blé", floor_price=180, ceiling_price=220, 
                      initial_price=200, initial_stock=0)
    crd.add_commodity("Cuivre", floor_price=8000, ceiling_price=12000,
                      initial_price=10000, initial_stock=0)
    crd.add_commodity("Coton", floor_price=70, ceiling_price=90,
                      initial_price=80, initial_stock=0)

    # Simuler des investissements de guildes
    guildes = [f"Guilde_{i}" for i in range(10)]
    for i, guild in enumerate(guildes):
        invest_amount = 10000 + i * 5000
        commodity = ["Blé", "Cuivre", "Coton"][i % 3]
        success = crd.invest_fulus(guild, invest_amount, commodity)
        if success:
            print(f"  {guild} a investi {invest_amount:,.0f} Fulus dans {commodity}")

    print(f"\n  Total CBU émis: {crd.cbu_supply:,.0f}")
    print(f"  Valeur des stocks: {crd.total_stock_value():,.0f}")
    print(f"  Taux d'adossement: {crd.get_backing_ratio():.3f}")
    print()

    # 3. Lois d'échelle urbaines
    print("[3] Lois d'échelle urbaines (Youn et al. 2014)")
    print("-" * 60)
    scaling = ScalingModel(eta=21.6, beta=0.92)

    populations = [100, 500, 1000, 5000, 10000, 50000]
    print(f"\n{'Population':>12} {'Établissements':>15} {'Diversité':>12} {'Production':>15}")
    print("-" * 60)
    for N in populations:
        metrics = scaling.compute_metrics(N)
        print(f"{N:>12,} {metrics['establishments']:>15,.0f} {metrics['diversity']:>12,.0f} {metrics['production_capacity']:>15,.0f}")
    print()

    # 4. Test de résistance des régimes
    print("[4] Test de résistance des régimes monétaires")
    print("-" * 60)
    df_comparison = compare_regimes()
    print(df_comparison.to_string(index=False))
    print()

    # 5. Scénarios de crise
    print("[5] Scénarios de crise")
    print("-" * 60)
    invasion_results = simulate_invasion_scenario(100)
    print(f"  Invasion - Masse finale: {invasion_results[-1]['money_supply']:.0f}")

    famine_results = simulate_famine_scenario(100)
    print(f"  Famine - Masse finale: {famine_results[-1]['money_supply']:.0f}")

    panic_results = simulate_panic_scenario(100)
    print(f"  Panique - Masse finale: {panic_results[-1]['money_supply']:.0f}")
    print()

    # 6. Paramètre de bifurcation
    print("[6] Paramètre de bifurcation Λ")
    print("-" * 60)
    entropy = PhysicalEntropy()

    debt = 1000
    interest_rate = 0.05
    low_entropy = 50

    lambda_val = entropy.bifurcation_parameter(debt, interest_rate, low_entropy)
    print(f"  Λ = {lambda_val:.3f}")
    print(f"  Statut: {'⚠️ COLLAPSOLOGIE' if lambda_val > 1 else '✅ STABLE'}")
    print()

    # 7. Détection d'absurdités chrématistiques
    print("[7] Détection d'absurdités chrématistiques")
    print("-" * 60)
    from core.entropy_physical import detect_chrematistic_absurdity

    wti_negative_price = -37.63
    energy_value = 7.2

    is_absurd = detect_chrematistic_absurdity(wti_negative_price, energy_value)
    print(f"  Prix WTI négatif (-37.63$) : {'⚠️ ABSURDE' if is_absurd else 'Normal'}")
    print()

    print("=" * 60)
    print("SIMULATION TERMINÉE")
    print("=" * 60)
    print("\nMécanisme purifié démontré:")
    print("  Guildes → Fulus → CRD → CBU → Guildes")
    print("  Cycle vertueux avec adossement physique")


if __name__ == "__main__":
    main()
