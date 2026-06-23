"""
Module d'inspection du marché (Hisba)
Régulation par le muhtassib

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class MarketViolation:
    """Violation détectée sur le marché"""
    type: str
    severity: float  # 0-1
    description: str
    evidence: Dict


class HisbaInstitution:
    """
    Institution de régulation du marché (Hisba)
    Inspirée du muhtassib traditionnel
    """

    def __init__(self):
        self.violations: List[MarketViolation] = []
        self.inspections: List[Dict] = []
        self.weights_and_measures: Dict[str, float] = {}
        self.fraud_scores: Dict[str, float] = {}

    def inspect_weights_and_measures(self, 
                                     item_name: str,
                                     declared_weight: float,
                                     actual_weight: float) -> bool:
        """Vérifie que les poids et mesures sont conformes"""
        tolerance = 0.01  # 1%
        is_valid = abs(declared_weight - actual_weight) <= tolerance * declared_weight

        if not is_valid:
            violation = MarketViolation(
                type='weight_fraud',
                severity=min(1.0, abs(declared_weight - actual_weight) / declared_weight),
                description=f"Poids déclaré {declared_weight} vs mesuré {actual_weight}",
                evidence={'item': item_name, 'declared': declared_weight, 'actual': actual_weight}
            )
            self.violations.append(violation)

        return is_valid

    def detect_market_manipulation(self, 
                                 prices: Dict[str, float],
                                 historical_prices: Dict[str, List[float]],
                                 threshold: float = 2.0) -> List[MarketViolation]:
        """Détecte les manipulations de marché (prix aberrants)"""
        violations = []

        for item, current_price in prices.items():
            if item not in historical_prices:
                continue

            hist = historical_prices[item]
            if len(hist) < 3:
                continue

            mean_price = np.mean(hist[-10:]) if len(hist) >= 10 else np.mean(hist)
            std_price = np.std(hist[-10:]) if len(hist) >= 10 else np.std(hist)

            if std_price > 0 and abs(current_price - mean_price) > threshold * std_price:
                violation = MarketViolation(
                    type='price_manipulation',
                    severity=min(1.0, abs(current_price - mean_price) / (threshold * std_price)),
                    description=f"Prix aberrant pour {item}: {current_price} vs moyenne {mean_price}",
                    evidence={'item': item, 'price': current_price, 'mean': mean_price}
                )
                violations.append(violation)
                self.violations.append(violation)

        return violations

    def inspect_fraudulent_bidding(self, 
                                 bids: List[float],
                                 ask: float) -> bool:
        """Détecte les enchères frauduleuses (najsh)"""
        if len(bids) < 2:
            return True

        mean_bid = np.mean(bids)
        max_bid = max(bids)

        if max_bid > mean_bid * 1.5 and max_bid > ask * 0.9:
            violation = MarketViolation(
                type='fraudulent_bidding',
                severity=min(1.0, (max_bid - mean_bid) / mean_bid),
                description=f"Enchère suspecte: max {max_bid} vs moyenne {mean_bid}",
                evidence={'bids': bids, 'ask': ask}
            )
            self.violations.append(violation)
            return False

        return True

    def get_honesty_score(self, merchant_id: str) -> float:
        """Calcule un score d'honnêteté pour un commerçant"""
        score = 1.0
        for v in self.violations:
            if merchant_id in str(v.evidence):
                score *= (1 - v.severity)

        self.fraud_scores[merchant_id] = score
        return score

    def report_annual(self) -> Dict:
        """Génère un rapport annuel d'inspection"""
        return {
            'total_violations': len(self.violations),
            'violations_by_type': {
                t: sum(1 for v in self.violations if v.type == t)
                for t in set(v.type for v in self.violations)
            },
            'average_severity': np.mean([v.severity for v in self.violations]) if self.violations else 0,
            'honesty_scores': self.fraud_scores
        }
