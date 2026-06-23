# simulation/diebold_mariano.py

import numpy as np
from scipy.stats import norm

def diebold_mariano_test(
    actual: np.ndarray,      # Valeurs réelles
    forecast1: np.ndarray,   # Prévisions du modèle 1 (CBU-X)
    forecast2: np.ndarray,   # Prévisions du modèle 2 (Référence)
    h: int = 1               # Horizon de prévision (pas de temps)
) -> dict:
    """
    Test de Diebold-Mariano pour comparer deux séries de prévisions.
    
    H0 : Les deux modèles ont la même précision prédictive.
    H1 : Les modèles ont des précisions différentes.
    """
    # Erreurs de prévision
    e1 = actual - forecast1
    e2 = actual - forecast2
    
    # Perte différentielle
    d = e1**2 - e2**2
    
    # Moyenne de la perte différentielle
    d_bar = np.mean(d)
    
    # Variance de la perte différentielle (avec correction pour autocorrélation)
    n = len(d)
    
    # Autocovariance à l'ordre k
    def autocovariance(x, k):
        return np.mean([(x[i] - np.mean(x)) * (x[i-k] - np.mean(x)) for i in range(k, len(x))])
    
    # Variance de Newey-West (avec fenêtre h)
    gamma_0 = np.var(d)
    gamma = 0
    for k in range(1, h + 1):
        gamma += 2 * (1 - k / (h + 1)) * autocovariance(d, k)
    
    var_d_bar = (gamma_0 + gamma) / n
    
    # Statistique DM
    if var_d_bar <= 0:
        dm_stat = 0
        p_value = 1.0
    else:
        dm_stat = d_bar / np.sqrt(var_d_bar)
        p_value = 2 * (1 - norm.cdf(abs(dm_stat)))  # Test bilatéral
    
    return {
        'dm_statistic': dm_stat,
        'p_value': p_value,
        'd_bar': d_bar,
        'mse1': np.mean(e1**2),
        'mse2': np.mean(e2**2),
        'significant': p_value < 0.05
    }


# Exemple d'utilisation
if __name__ == "__main__":
    np.random.seed(42)
    n = 26  # 26 années (2000-2025)
    
    # Valeurs réelles simulées (inflation réelle)
    actual = 0.02 + 0.01 * np.random.randn(n)
    
    # Prévisions CBU-X (meilleures)
    forecast_cbu = actual + 0.005 * np.random.randn(n)
    
    # Prévisions de référence (moins bonnes)
    forecast_ref = actual + 0.015 * np.random.randn(n)
    
    result = diebold_mariano_test(actual, forecast_cbu, forecast_ref, h=1)
    
    print("=== TEST DE DIEBOLD-MARIANO ===")
    print(f"DM Statistic : {result['dm_statistic']:.4f}")
    print(f"p-value      : {result['p_value']:.4f}")
    print(f"MSE CBU-X    : {result['mse1']:.6f}")
    print(f"MSE Référence: {result['mse2']:.6f}")
    print(f"Amélioration : {(1 - result['mse1']/result['mse2']) * 100:.1f}%")
    print(f"Significatif  : {'✅ OUI' if result['significant'] else '❌ NON'}")
