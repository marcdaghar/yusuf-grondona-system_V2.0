"""
Module de Zakat simplifié

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from typing import List
from dataclasses import dataclass


@dataclass
class ZakatPayer:
    """Payeur de Zakat"""
    name: str
    wealth: float
    gold_grams: float
    silver_grams: float


def calculate_zakat(
    nuqud_holdings: List,
    trade_profit_nuqud: float,
    agricultural_yield_nuqud: float,
    livestock_nuqud: float
) -> float:
    """
    Calcule la Zakat due en nuqud

    Taux:
    - Or/argent/cash: 2.5% (1/40)
    - Produits agricoles: 10% (arrosage naturel) ou 5% (arrosage artificiel)
    - Bétail: seuils spécifiques
    """
    total = 0.0

    # Zakat sur l'épargne (nuqud)
    for n in nuqud_holdings:
        if hasattr(n, 'is_zakatable') and n.is_zakatable():
            total += n.value_in_silver_grams() * 0.025

    # Zakat sur le profit du commerce
    total += trade_profit_nuqud * 0.025

    # Zakat sur les produits agricoles (10%)
    total += agricultural_yield_nuqud * 0.10

    # Zakat sur le bétail (simplifié)
    total += livestock_nuqud * 0.025

    return total
