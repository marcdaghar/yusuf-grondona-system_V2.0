"""
Lois d'échelle urbaines pour la production des guildes
Basé sur Youn et al. (2014) — Universal urban economic diversity

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List


class ScalingModel:
    """
    Modèle de diversité économique urbaine

    Lois d'échelle:
    - N_f = η · N (nombre d'établissements)
    - N_sector = N^β_c (diversité sectorielle)
    - β ≈ 0.92 (exposant universel)
    """

    def __init__(self, eta: float = 21.6, beta: float = 0.92):
        """
        Args:
            eta: Constante universelle (≈ 21.6)
            beta: Exposant de diversité (≈ 0.92)
        """
        self.eta = eta
        self.beta = beta

        # Exposants sectoriels (Youn et al. 2014)
        self.beta_sectors = {
            'finance': 1.12,
            'technology': 1.08,
            'retail': 1.02,
            'manufacturing': 0.95,
            'agriculture': 0.82,
            'construction': 0.88,
            'healthcare': 0.92,
            'education': 0.85,
            'hospitality': 1.05,
            'transportation': 0.90,
            'mining': 0.78,
            'textile': 0.88,
            'food_processing': 0.93
        }

    def establishments(self, N: float) -> float:
        """
        Nombre total d'établissements
        N_f = η · N
        """
        return self.eta * N

    def sector_diversity(self, N: float, sector: str) -> float:
        """
        Diversité sectorielle
        N_sector = N^β_c
        """
        beta_c = self.beta_sectors.get(sector, self.beta)
        return N ** beta_c

    def diversity(self, N: float) -> float:
        """
        Diversité économique totale (moyenne géométrique)
        """
        diversities = [N ** b for b in self.beta_sectors.values()]
        return np.exp(np.mean(np.log(diversities)))

    def government_size(self, N: float, beta_G: float = 0.85) -> float:
        """
        Taille du gouvernement (administration)
        """
        return N ** beta_G

    def governance_efficiency(self, N: float, beta_G: float = 0.85) -> float:
        """
        Efficacité de gouvernance
        N^(β - β_G)
        """
        return N ** (self.beta - beta_G)

    def compute_metrics(self, N: float, beta_G: float = 0.85) -> Dict:
        """
        Calcule toutes les métriques de scaling
        """
        return {
            'population': N,
            'establishments': self.establishments(N),
            'diversity': self.diversity(N),
            'government_size': self.government_size(N, beta_G),
            'governance_efficiency': self.governance_efficiency(N, beta_G),
            'production_capacity': self.establishments(N) * self.diversity(N)
        }

    def rank_abundance(self, ranks: np.ndarray, 
                       gamma: float = 0.49, 
                       x0: float = 211) -> np.ndarray:
        """
        Distribution rang-abondance
        f(x) = A · x^(-γ) · exp(-x/x0)
        """
        A = 1.0
        return A * ranks ** (-gamma) * np.exp(-ranks / x0)

    def shannon_diversity(self, proportions: List[float]) -> float:
        """
        Indice de diversité de Shannon
        H = -Σ p_i · ln(p_i)
        """
        proportions = np.array(proportions)
        proportions = proportions[proportions > 0]
        return -np.sum(proportions * np.log(proportions))
