"""
Système d'alerte précoce pour les crises

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple


class EarlyWarningSystem:
    """Système d'alerte précoce basé sur les signaux faibles"""

    def __init__(self, warning_thresholds: Dict[str, float] = None):
        self.thresholds = warning_thresholds or {
            'lambda_bifurcation': 0.7,
            'gini_coefficient': 0.35,
            'trust_index': 0.75,
            'entropy_rate': 0.5,
            'default_rate': 0.1
        }
        self.history: List[Dict] = []

    def compute_risk_score(self, indicators: Dict[str, float]) -> float:
        """Calcule un score de risque global"""
        scores = []
        weights = {
            'lambda_bifurcation': 0.3,
            'gini_coefficient': 0.2,
            'trust_index': 0.2,
            'entropy_rate': 0.15,
            'default_rate': 0.15
        }

        for key, value in indicators.items():
            if key in self.thresholds:
                normalized = value / self.thresholds[key]
                scores.append(normalized * weights.get(key, 0.1))

        return sum(scores) / sum(weights.values()) if scores else 0.0

    def assess_crisis_probability(self, 
                                  current_state: Dict,
                                  historical_states: List[Dict]) -> float:
        """Évalue la probabilité de crise basée sur l'historique"""
        if len(historical_states) < 10:
            return 0.0

        current_score = self.compute_risk_score(current_state)
        historical_scores = [self.compute_risk_score(s) for s in historical_states]

        mean_score = np.mean(historical_scores)
        std_score = np.std(historical_scores)

        if std_score == 0:
            return 0.0

        z_score = (current_score - mean_score) / std_score
        probability = 1 / (1 + np.exp(-z_score))

        return probability

    def generate_alert(self, state: Dict) -> Dict:
        """Génère une alerte complète"""
        risk_score = self.compute_risk_score(state)

        alert_level = "NORMAL"
        if risk_score > 1.5:
            alert_level = "CRITIQUE"
        elif risk_score > 1.0:
            alert_level = "ÉLEVÉ"
        elif risk_score > 0.7:
            alert_level = "MODÉRÉ"

        triggered_indicators = {
            k: v for k, v in state.items()
            if k in self.thresholds and v > self.thresholds[k]
        }

        alert = {
            'timestamp': None,
            'risk_score': risk_score,
            'alert_level': alert_level,
            'triggered_indicators': triggered_indicators,
            'recommended_actions': self._recommend_actions(triggered_indicators)
        }

        self.history.append(alert)
        return alert

    def _recommend_actions(self, triggered: Dict[str, float]) -> List[str]:
        """Recommande des actions basées sur les indicateurs déclenchés"""
        actions = []

        if 'lambda_bifurcation' in triggered:
            actions.append("Réduire la dette agrégée ou augmenter l'extraction d'entropie basse")

        if 'gini_coefficient' in triggered:
            actions.append("Activer le mécanisme de redistribution Zakat")

        if 'trust_index' in triggered:
            actions.append("Renforcer la transparence du netting et des réserves")

        if 'entropy_rate' in triggered:
            actions.append("Optimiser la logistique pour réduire les pertes physiques")

        if 'default_rate' in triggered:
            actions.append("Activer le mécanisme de gel gradué du CRD")

        return actions
