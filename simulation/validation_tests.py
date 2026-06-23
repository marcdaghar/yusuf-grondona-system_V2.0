# simulation/validation_tests.py

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from scipy.stats import norm

class ModelValidator:
    """
    Valide les modèles CBU-X avec :
    - Matrice de confusion pour la détection de crises
    - Test de Diebold-Mariano pour la précision des prévisions
    """
    
    def __init__(self, actual_crises, predicted_crises, actual_inflation, pred_cbu, pred_ref):
        self.actual_crises = actual_crises
        self.predicted_crises = predicted_crises
        self.actual_inflation = actual_inflation
        self.pred_cbu = pred_cbu
        self.pred_ref = pred_ref
    
    def confusion_matrix_analysis(self):
        """Analyse de la matrice de confusion"""
        tn, fp, fn, tp = confusion_matrix(self.actual_crises, self.predicted_crises).ravel()
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        return {
            'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'precision': precision,
            'f1_score': f1
        }
    
    def diebold_mariano(self, h=1):
        """Test de Diebold-Mariano"""
        e1 = self.actual_inflation - self.pred_cbu
        e2 = self.actual_inflation - self.pred_ref
        
        d = e1**2 - e2**2
        d_bar = np.mean(d)
        n = len(d)
        
        def autocov(x, k):
            return np.mean([(x[i] - np.mean(x)) * (x[i-k] - np.mean(x)) for i in range(k, len(x))])
        
        gamma_0 = np.var(d)
        gamma = sum([2 * (1 - k / (h + 1)) * autocov(d, k) for k in range(1, h + 1)])
        var_d_bar = (gamma_0 + gamma) / n
        
        dm_stat = d_bar / np.sqrt(var_d_bar) if var_d_bar > 0 else 0
        p_value = 2 * (1 - norm.cdf(abs(dm_stat)))
        
        return {
            'dm_statistic': dm_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'mse_cbu': np.mean(e1**2),
            'mse_ref': np.mean(e2**2)
        }
    
    def full_report(self):
        """Rapport complet de validation"""
        cm = self.confusion_matrix_analysis()
        dm = self.diebold_mariano()
        
        return {
            'confusion_matrix': cm,
            'diebold_mariano': dm,
            'summary': {
                'crisis_detection': '✅' if cm['sensitivity'] > 0.9 and cm['specificity'] > 0.8 else '⚠️',
                'forecast_improvement': f"{100 - (dm['mse_cbu']/dm['mse_ref'])*100:.1f}%",
                'dm_significant': dm['significant']
            }
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Données simulées
    np.random.seed(42)
    n = 103  # 2000-2025 (périodes mensuelles)
    
    actual_crises = [False] * n
    actual_crises[96] = True   # 2008
    actual_crises[240] = True  # 2020
    actual_crises[264] = True  # 2022
    
    predicted_crises = [False] * n
    predicted_crises[96] = True
    predicted_crises[240] = True
    predicted_crises[264] = True
    predicted_crises[180] = True  # Fausse alerte 2015
    predicted_crises[216] = True  # Fausse alerte 2018
    
    # Inflation (26 années)
    actual_inf = 0.02 + 0.008 * np.random.randn(26)
    pred_cbu = actual_inf + 0.004 * np.random.randn(26)
    pred_ref = actual_inf + 0.012 * np.random.randn(26)
    
    validator = ModelValidator(actual_crises, predicted_crises, actual_inf, pred_cbu, pred_ref)
    report = validator.full_report()
    
    print("=== RAPPORT DE VALIDATION ===")
    print("\nMatrice de confusion:")
    print(f"  TP: {report['confusion_matrix']['TP']}, FP: {report['confusion_matrix']['FP']}")
    print(f"  FN: {report['confusion_matrix']['FN']}, TN: {report['confusion_matrix']['TN']}")
    print(f"  Sensibilité: {report['confusion_matrix']['sensitivity']:.2f}")
    print(f"  Spécificité: {report['confusion_matrix']['specificity']:.2f}")
    print(f"  F1-Score: {report['confusion_matrix']['f1_score']:.2f}")
    
    print("\nTest de Diebold-Mariano:")
    print(f"  DM Statistic: {report['diebold_mariano']['dm_statistic']:.3f}")
    print(f"  p-value: {report['diebold_mariano']['p_value']:.4f}")
    print(f"  Amélioration CBU-X: {report['summary']['forecast_improvement']}")
    print(f"  Significatif: {report['summary']['dm_significant']}")
