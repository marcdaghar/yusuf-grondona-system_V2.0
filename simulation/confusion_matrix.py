# simulation/confusion_matrix.py

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

def compute_crisis_confusion_matrix(
    predicted_crises: list,  # Liste de booléens (True = crise prédite)
    actual_crises: list      # Liste de booléens (True = crise réelle)
) -> dict:
    """
    Calcule la matrice de confusion pour la détection de crises.
    """
    tn, fp, fn, tp = confusion_matrix(actual_crises, predicted_crises).ravel()
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
    
    return {
        'confusion_matrix': {'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn},
        'sensitivity': sensitivity,
        'specificity': specificity,
        'precision': precision,
        'f1_score': f1_score
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # Historique 2000-2025 (simulé)
    actual = [False] * 103  # 103 périodes
    actual[8] = True   # 2008
    actual[20] = True  # 2020
    actual[22] = True  # 2022
    
    predicted = [False] * 103
    predicted[8] = True
    predicted[20] = True
    predicted[22] = True
    predicted[15] = True  # Fausse alerte 2015
    predicted[18] = True  # Fausse alerte 2018
    
    results = compute_crisis_confusion_matrix(predicted, actual)
    print("Matrice de confusion pour la détection de crises :")
    print(f"  Vrais Positifs : {results['confusion_matrix']['TP']}")
    print(f"  Faux Positifs  : {results['confusion_matrix']['FP']}")
    print(f"  Faux Négatifs  : {results['confusion_matrix']['FN']}")
    print(f"  Vrais Négatifs : {results['confusion_matrix']['TN']}")
    print(f"\nSensibilité : {results['sensitivity']:.2f}")
    print(f"Spécificité  : {results['specificity']:.2f}")
    print(f"Précision    : {results['precision']:.2f}")
    print(f"F1-Score     : {results['f1_score']:.2f}")
