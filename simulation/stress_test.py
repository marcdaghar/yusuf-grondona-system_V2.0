"""
Module de test de résistance comparant les régimes monétaires

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from simulation.agents import MonetaryModel


def run_stress_test(regime: str, 
                    n_agents: int = 100, 
                    steps: int = 500,
                    shocks: List[Tuple[int, float]] = None) -> Dict:
    """
    Exécute un test de résistance pour un régime donné
    """
    model = MonetaryModel(n_agents=n_agents, regime=regime)

    if shocks is None:
        shocks = [
            (100, 0.2),
            (250, 0.3),
            (400, 0.15)
        ]

    for step in range(steps):
        shock = 0
        for period, intensity in shocks:
            if step == period:
                shock = intensity
                break

        model.step(shock_intensity=shock)

    data = model.datacollector.get_model_vars_dataframe()

    return {
        'regime': regime,
        'final_gdp': data['GDP'].iloc[-1],
        'mean_gdp': data['GDP'].mean(),
        'gini': data['Gini'].iloc[-1],
        'default_rate': data['DefaultRate'].iloc[-1],
        'total_debt': data['TotalDebt'].iloc[-1],
        'entropy': data['Entropy'].iloc[-1],
        'data': data
    }


def compare_regimes() -> pd.DataFrame:
    """Compare les différents régimes"""
    regimes = [
        'fiat',
        'gold_standard',
        'islamic_no_interest',
        'islamic_no_interest_zakat'
    ]

    results = []
    for regime in regimes:
        result = run_stress_test(regime)
        results.append(result)

    df = pd.DataFrame([
        {
            'Regime': r['regime'],
            'GDP Final': r['final_gdp'],
            'GDP Moyen': r['mean_gdp'],
            'Gini': r['gini'],
            'Default Rate': r['default_rate'],
            'Total Debt': r['total_debt'],
            'Entropy': r['entropy']
        }
        for r in results
    ])

    return df


if __name__ == "__main__":
    df = compare_regimes()
    print("\n=== COMPARAISON DES RÉGIMES MONÉTAIRES ===\n")
    print(df.to_string(index=False))
