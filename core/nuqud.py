"""
Module de gestion des nuqud (monnaie-marchandise or/argent)

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class NuqudReserve:
    """Réserves de nuqud (or/argent)"""
    gold_grams: float = 0.0
    silver_grams: float = 0.0
    gold_price_per_gram: float = 55.0  # USD
    silver_price_per_gram: float = 0.75  # USD

    def total_value_usd(self) -> float:
        """Calcule la valeur totale des réserves en USD"""
        gold_value = self.gold_grams * self.gold_price_per_gram
        silver_value = self.silver_grams * self.silver_price_per_gram
        return gold_value + silver_value

    def value_in_cbu(self, cbu_price_usd: float) -> float:
        """Calcule la valeur en CBU (Commodity Basket Unit)"""
        if cbu_price_usd == 0:
            return 0.0
        return self.total_value_usd() / cbu_price_usd

    def add_gold(self, grams: float) -> None:
        self.gold_grams += grams

    def add_silver(self, grams: float) -> None:
        self.silver_grams += grams

    def withdraw_gold(self, grams: float) -> bool:
        if self.gold_grams >= grams:
            self.gold_grams -= grams
            return True
        return False

    def withdraw_silver(self, grams: float) -> bool:
        if self.silver_grams >= grams:
            self.silver_grams -= grams
            return True
        return False
