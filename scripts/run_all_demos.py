#!/usr/bin/env python3
"""
Script pour exécuter toutes les démonstrations du système

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.run_full import main as run_full_simulation
from simulation.yusuf_model import YusufConfig, ScenarioComparator
from core.grondona_crd import GrondonaCRD, simulate_crd
from core.entropy_physical import PhysicalEntropy


def demo_yusuf_vs_capitalist():
    """Démonstration: Yusuf vs Capitaliste"""
    print("\n" + "="*60)
    print("DÉMO 1: Yusuf Counter-Cycle vs Capitalist System")
    print("="*60)

    config = YusufConfig(T=50, dt=0.5)
    comparator = ScenarioComparator(config)
    y_res, c_res = comparator.run_single()

    print(f"\nYusuf final stock:     {y_res.final_stock:.2f}")
    print(f"Capitalist final stock: {c_res.final_stock:.2f}")
    print(f"Yusuf solvency:        {y_res.solvency_rate:.1f}%")
    print(f"Capitalist solvency:    {c_res.solvency_rate:.1f}%")
    print(f"Improvement:            +{(y_res.solvency_rate - c_res.solvency_rate):.1f} pp")


def demo_grondona_crd():
    """Démonstration: CRD Grondona"""
    print("\n" + "="*60)
    print("DÉMO 2: Grondona Commodity Reserve Department")
    print("="*60)

    initial_prices = {
        "Blé": 200,
        "Cuivre": 10000,
        "Coton": 80,
        "Or": 1800,
        "Pétrole": 70
    }

    results = simulate_crd(initial_prices, periods=100, price_volatility=0.2)

    print(f"\nInitial money supply:  0")
    print(f"Final money supply:      {results[-1]['money_supply']:.0f}")
    print(f"Final stock value:       {results[-1]['total_value']:.0f}")
    print(f"Price volatility:        {np.std([r['money_supply'] for r in results]):.0f}")


def demo_entropy():
    """Démonstration: Entropie et paramètre Λ"""
    print("\n" + "="*60)
    print("DÉMO 3: Thermodynamic Entropy & Bifurcation Parameter")
    print("="*60)

    entropy = PhysicalEntropy()

    # Stable system
    lambda_stable = entropy.bifurcation_parameter(100, 0.03, 10)
    print(f"\nStable system (D=100, r=3%, E=10):")
    print(f"  Λ = {lambda_stable:.3f} {'✅ STABLE' if lambda_stable < 1 else '⚠️ COLLAPSE'}")

    # Unstable system
    lambda_unstable = entropy.bifurcation_parameter(1000, 0.05, 10)
    print(f"\nUnstable system (D=1000, r=5%, E=10):")
    print(f"  Λ = {lambda_unstable:.3f} {'✅ STABLE' if lambda_unstable < 1 else '⚠️ COLLAPSE'}")

    # Critical interest rate
    critical_rate = entropy.find_critical_interest_rate(100, 10)
    print(f"\nCritical interest rate for D=100, E=10: {critical_rate:.4f}")


def demo_full_simulation():
    """Démonstration: Simulation complète"""
    print("\n" + "="*60)
    print("DÉMO 4: Full System Simulation")
    print("="*60)
    run_full_simulation()


def main():
    print("\n" + "="*60)
    print("YUSUF-GRONDONA SYSTEM — ALL DEMOS")
    print("="*60)

    import numpy as np

    demo_yusuf_vs_capitalist()
    demo_grondona_crd()
    demo_entropy()
    demo_full_simulation()

    print("\n" + "="*60)
    print("ALL DEMOS COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("  • Run dashboard:  streamlit run dashboard/streamlit_app.py")
    print("  • Run tests:      pytest tests/ -v")
    print("  • Read article:     docs/CBU-X_v2.0_Article.md")


if __name__ == "__main__":
    main()
