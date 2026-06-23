"""
Cycle vertueux: Guildes → Fulus → CRD → CBU → Guildes

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

from core.scaling_model import ScalingModel
from core.grondona_crd import GrondonaCRD


@dataclass
class CycleResult:
    """Résultat d'une étape du cycle"""
    period: int
    fulus_produced: float
    invested: float
    quantity_bought: float
    cbu_issued: float
    reinvested: float
    new_fulus: float
    backing_ratio: float
    population: float


class GuildCRDCycle:
    """
    Cycle Guildes → Fulus → CRD → CBU → Guildes

    Paramètres:
    - eta: Constante universelle (21.6)
    - beta: Exposant de diversité (0.92)
    - lambda_invest: Taux d'investissement (0.7 = 70%)
    - kappa: Taux de couverture CBU (0.8 = 80%)
    - rho: Taux de réinvestissement (0.5 = 50%)
    """

    def __init__(self, 
                 eta: float = 21.6, 
                 beta: float = 0.92, 
                 lambda_invest: float = 0.7,
                 kappa: float = 0.8, 
                 rho: float = 0.5,
                 commodity_price: float = 100.0):

        self.eta = eta
        self.beta = beta
        self.lambda_invest = lambda_invest
        self.kappa = kappa
        self.rho = rho
        self.price = commodity_price

        self.scaling = ScalingModel(eta=eta, beta=beta)
        self.crd = GrondonaCRD(coverage_rate=kappa)

        # Initialiser les commodités du CRD
        self.crd.add_commodity("blé", floor_price=80, ceiling_price=120, 
                               initial_price=100, initial_stock=0)
        self.crd.add_commodity("cuivre", floor_price=8000, ceiling_price=12000,
                               initial_price=10000, initial_stock=0)
        self.crd.add_commodity("or", floor_price=1600, ceiling_price=2200,
                               initial_price=1800, initial_stock=0)
        self.crd.add_commodity("argent", floor_price=20, ceiling_price=30,
                               initial_price=25, initial_stock=0)
        self.crd.add_commodity("pétrole", floor_price=60, ceiling_price=80,
                               initial_price=70, initial_stock=0)

        self.history: List[CycleResult] = []

    def step(self, N: float, guild_id: str = "guild_1") -> CycleResult:
        """
        Une étape du cycle

        Args:
            N: Population de la guilde
            guild_id: Identifiant de la guilde

        Returns:
            Résultat de l'étape
        """
        # 1. Production de Fulus par la guilde
        # F = η · N · N^β
        fulus = self.eta * N * (N ** self.beta)

        # 2. Investissement dans le CRD (70%)
        invest = self.lambda_invest * fulus

        # 3. Achat de commodités et émission de CBU
        # On diversifie l'investissement sur plusieurs commodités
        commodities = list(self.crd.commodities.keys())
        invest_per_commodity = invest / len(commodities)

        total_cbu = 0
        total_quantity = 0

        for commodity in commodities:
            success = self.crd.invest_fulus(guild_id, invest_per_commodity, commodity)
            if success and guild_id in self.crd.investments:
                inv = self.crd.investments[guild_id]
                total_cbu += inv.cbu_issued
                total_quantity += inv.quantity

        # 4. Réinvestissement (50% des CBU)
        reinvest = self.rho * total_cbu

        # 5. Mise à jour de la guilde
        # Les Fulus restants + les CBU non réinvestis
        new_fulus = fulus * (1 - self.lambda_invest) + total_cbu * (1 - self.rho)

        # 6. Croissance de la population (effet de l'investissement)
        population_growth = 1 + 0.01 * total_cbu / (N * 10)
        new_N = N * population_growth

        result = CycleResult(
            period=len(self.history),
            fulus_produced=fulus,
            invested=invest,
            quantity_bought=total_quantity,
            cbu_issued=total_cbu,
            reinvested=reinvest,
            new_fulus=new_fulus,
            backing_ratio=self.crd.get_backing_ratio(),
            population=new_N
        )

        self.history.append(result)
        return result

    def run_simulation(self, N0: float = 1000, n_steps: int = 50) -> List[CycleResult]:
        """
        Simulation sur plusieurs périodes

        Args:
            N0: Population initiale
            n_steps: Nombre de périodes

        Returns:
            Liste des résultats
        """
        N = N0

        for step in range(n_steps):
            result = self.step(N)
            N = result.population

        return self.history

    def get_summary(self) -> Dict:
        """Résumé de la simulation"""
        if not self.history:
            return {}

        total_fulus = sum(r.fulus_produced for r in self.history)
        total_cbu = sum(r.cbu_issued for r in self.history)
        total_invested = sum(r.invested for r in self.history)

        return {
            'n_periods': len(self.history),
            'initial_population': self.history[0].population if self.history else 0,
            'final_population': self.history[-1].population if self.history else 0,
            'total_fulus_produced': total_fulus,
            'total_cbu_issued': total_cbu,
            'total_invested': total_invested,
            'average_backing_ratio': np.mean([r.backing_ratio for r in self.history]),
            'final_backing_ratio': self.history[-1].backing_ratio if self.history else 0,
            'population_growth': (self.history[-1].population / self.history[0].population - 1) * 100 if self.history else 0
        }

    def export_to_dataframe(self):
        """Exporte l'historique en DataFrame"""
        import pandas as pd

        data = []
        for r in self.history:
            data.append({
                'period': r.period,
                'fulus_produced': r.fulus_produced,
                'invested': r.invested,
                'quantity_bought': r.quantity_bought,
                'cbu_issued': r.cbu_issued,
                'reinvested': r.reinvested,
                'new_fulus': r.new_fulus,
                'backing_ratio': r.backing_ratio,
                'population': r.population
            })

        return pd.DataFrame(data)


def demonstrate_cycle():
    """Démonstration du cycle avec paramètres par défaut"""
    print("=" * 60)
    print("CYCLE GUILDES → FULUS → CRD → CBU → GUILDES")
    print("=" * 60)

    # Paramètres
    N0 = 1000  # Population initiale
    eta = 21.6  # Constante universelle
    beta = 0.92  # Exposant de diversité
    lambda_inv = 0.7  # 70% investi
    kappa = 0.8  # 80% couverture
    rho = 0.5  # 50% réinvesti
    price = 100.0  # Prix de référence

    print(f"\nParamètres:")
    print(f"  Population initiale: {N0}")
    print(f"  η (constante): {eta}")
    print(f"  β (diversité): {beta}")
    print(f"  λ (investissement): {lambda_inv}")
    print(f"  κ (couverture): {kappa}")
    print(f"  ρ (réinvestissement): {rho}")
    print(f"  Prix commodité: {price}")

    # Calcul manuel de la première étape
    print(f"\n--- Étape 1 ---")
    fulus = eta * N0 * (N0 ** beta)
    print(f"  Fulus produits: {fulus:,.0f}")

    invest = lambda_inv * fulus
    print(f"  Investissement (70%): {invest:,.0f}")

    quantity = invest / price
    print(f"  Quantité achetée: {quantity:,.0f} unités")

    cbu = kappa * quantity * price
    print(f"  CBU émis (80%): {cbu:,.0f}")

    reinvest = rho * cbu
    print(f"  Réinvesti (50%): {reinvest:,.0f}")

    new_fulus = fulus * (1 - lambda_inv) + cbu * (1 - rho)
    print(f"  Nouveaux Fulus: {new_fulus:,.0f}")

    # Simulation complète
    print(f"\n--- Simulation sur 20 périodes ---")
    cycle = GuildCRDCycle(
        eta=eta, beta=beta, 
        lambda_invest=lambda_inv, 
        kappa=kappa, rho=rho,
        commodity_price=price
    )

    results = cycle.run_simulation(N0=N0, n_steps=20)
    summary = cycle.get_summary()

    print(f"\nRésumé:")
    print(f"  Population initiale: {summary['initial_population']:,.0f}")
    print(f"  Population finale: {summary['final_population']:,.0f}")
    print(f"  Croissance: {summary['population_growth']:+.1f}%")
    print(f"  Fulus totaux produits: {summary['total_fulus_produced']:,.0f}")
    print(f"  CBU totaux émis: {summary['total_cbu_issued']:,.0f}")
    print(f"  Taux d'adossement moyen: {summary['average_backing_ratio']:.3f}")
    print(f"  Taux d'adossement final: {summary['final_backing_ratio']:.3f}")

    print(f"\n" + "=" * 60)
    print("CYCLE VERTUEUX DÉMONTRÉ")
    print("=" * 60)

    return cycle


if __name__ == "__main__":
    demonstrate_cycle()
