"""
Module d'entropie informationnelle (Shannon)
Mesure le désordre dans les systèmes de prix

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import List, Dict


class ShannonEntropy:
    """
    Calcule l'entropie informationnelle de Shannon
    """

    @staticmethod
    def price_entropy(prices: List[float], reference_price: float = None) -> float:
        """
        Calcule l'entropie des prix
        H = -Σ(p_i / p̄) * ln(p_i / p̄)
        """
        if not prices:
            return 0.0

        if reference_price is None:
            reference_price = np.mean(prices)

        if reference_price == 0:
            return 0.0

        normalized = np.array(prices) / reference_price
        valid = normalized > 0
        if not any(valid):
            return 0.0

        normalized = normalized[valid]
        entropy = -np.sum(normalized * np.log(normalized))

        return entropy

    @staticmethod
    def exchange_rate_entropy(rates: Dict[str, float], base_rate: float = None) -> float:
        """Calcule l'entropie des taux de change"""
        if not rates:
            return 0.0

        values = list(rates.values())
        return ShannonEntropy.price_entropy(values, base_rate)

    @staticmethod
    def transaction_entropy(transactions: List[float]) -> float:
        """
        Calcule l'entropie des montants de transaction
        Mesure la diversité des transactions
        """
        if not transactions:
            return 0.0

        total = sum(transactions)
        if total == 0:
            return 0.0

        probabilities = np.array(transactions) / total
        probabilities = probabilities[probabilities > 0]
        entropy = -np.sum(probabilities * np.log(probabilities))

        return entropy
