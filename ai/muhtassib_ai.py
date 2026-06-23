"""
Module d'IA assistante pour le muhtassib
Détection d'anomalies et signaux faibles

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional


class MuhtassibAI:
    """
    Intelligence artificielle assistante pour le muhtassib
    - Détection d'anomalies (Isolation Forest)
    - Détection de signaux faibles
    - Coordination logistique
    """

    def __init__(self, contamination: float = 0.1):
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.anomaly_threshold = -0.5

    def fit(self, data: np.ndarray) -> None:
        """Entraîne le modèle sur des données historiques"""
        scaled_data = self.scaler.fit_transform(data)
        self.isolation_forest.fit(scaled_data)
        self.is_fitted = True

    def detect_anomalies(self, data: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """
        Détecte les anomalies dans les données

        Returns:
            (scores, indices_anomalies)
        """
        if not self.is_fitted:
            return np.array([]), []

        scaled_data = self.scaler.transform(data)
        scores = self.isolation_forest.decision_function(scaled_data)
        anomalies = np.where(scores < self.anomaly_threshold)[0]

        return scores, anomalies.tolist()

    def detect_market_anomalies(self, 
                                prices: Dict[str, float],
                                historical: Dict[str, List[float]]) -> Dict[str, bool]:
        """Détecte les anomalies de marché"""
        anomalies = {}

        for item, current_price in prices.items():
            if item not in historical:
                continue

            hist = historical[item]
            if len(hist) < 10:
                continue

            mean_price = np.mean(hist[-20:])
            std_price = np.std(hist[-20:])

            if std_price > 0:
                z_score = abs(current_price - mean_price) / std_price
                anomalies[item] = z_score > 3.0
            else:
                anomalies[item] = False

        return anomalies

    def detect_weak_signals(self, 
                           data: Dict,
                           thresholds: Dict[str, float]) -> Dict[str, float]:
        """Détecte les signaux faibles (prédictions de crise)"""
        signals = {}

        if 'volatility' in data:
            signals['stress_volatility'] = data['volatility'] / thresholds.get('volatility', 0.1)

        if 'debt_ratio' in data:
            signals['debt_stress'] = data['debt_ratio'] / thresholds.get('debt_ratio', 0.6)

        if 'inventory_level' in data:
            signals['inventory_stress'] = 1.0 - data['inventory_level'] / thresholds.get('inventory', 1.0)

        return signals

    def suggest_coordination(self, 
                            warehouse_stocks: Dict[str, float],
                            demand_forecast: Dict[str, float]) -> Dict[str, str]:
        """Suggère des actions de coordination logistique"""
        suggestions = {}

        for warehouse, stock in warehouse_stocks.items():
            if warehouse in demand_forecast:
                demand = demand_forecast[warehouse]
                if stock < demand * 1.2:
                    suggestions[warehouse] = f"Réapprovisionnement urgent (stock {stock:.0f}, demande {demand:.0f})"
                elif stock > demand * 3:
                    suggestions[warehouse] = f"Excédent de stock (réduire commandes)"
                else:
                    suggestions[warehouse] = "Niveau normal"

        return suggestions

    def alert_muhtassib(self, 
                       anomalies: List[str],
                       weak_signals: Dict[str, float],
                       threshold: float = 0.8) -> Dict[str, str]:
        """Génère des alertes pour le muhtassib"""
        alerts = {}

        for anomaly in anomalies:
            alerts[f"ANOMALIE_{anomaly}"] = "Critique"

        for signal, value in weak_signals.items():
            if value > threshold:
                alerts[f"SIGNAL_{signal}"] = f"Alerte (niveau {value:.2f})"

        return alerts
