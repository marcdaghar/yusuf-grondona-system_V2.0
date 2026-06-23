# Mécanisme Purifié : Guildes → Fulus → CRD → CBU

## Vue d'ensemble

Le mécanisme purifié du système Yusuf-Grondona repose sur un **cycle vertueux** où les guildes productives génèrent des Fulus, les investissent dans le CRD (Commodity Reserve Department), qui émet des CBU adossés à des stocks physiques de commodités.

## Flux Économique

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. GUILDES (Productrices)                                  │
│     ├── Population (N)                                       │
│     ├── Établissements (N_f = η·N)                          │
│     ├── Diversité sectorielle (N^β_c)                       │
│     └── Production de Fulus = η·N·N^β                       │
│          ↓                                                   │
│  2. INVESTISSEMENT dans le CRD (70% des Fulus)              │
│          ↓                                                   │
│  3. CRD (Régulateur)                                         │
│     ├── Achat de commodités (blé, cuivre, or, argent, pétrole)
│     ├── Constitution de stocks physiques                    │
│     ├── Émission de CBU (80% de couverture)                 │
│     └── Régulation des prix (floor/ceiling)                  │
│          ↓                                                   │
│  4. RETOUR aux Guildes                                       │
│     ├── CBU pour le commerce inter-guildes                  │
│     ├── Plus-value sur les stocks                           │
│     └── 50% réinvesti dans le CRD                           │
│          ↓                                                   │
│  CYCLE VERTUEUX                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Équations Structurantes

### Production de Fulus

```
F = η · N · N^β
```

- **F** = Fulus produits
- **η** = 21.6 (constante universelle)
- **N** = Population de la guilde
- **β** = 0.92 (exposant de diversité)

### Investissement

```
I = λ · F
```

- **I** = Montant investi
- **λ** = 0.70 (70% des Fulus)

### Émission de CBU

```
CBU = κ · I / P
```

- **CBU** = Unités émises
- **κ** = 0.80 (80% de couverture)
- **P** = Prix de la commodité

### Réinvestissement

```
F_{t+1} = F_t + ρ · CBU_t
```

- **ρ** = 0.50 (50% des CBU réinvestis)

## Implémentation Python

Voir les modules :
- `core/scaling_model.py` — Lois d'échelle urbaines
- `core/grondona_crd.py` — CRD avec investissement des guildes
- `core/guild_crd_cycle.py` — Cycle vertueux complet

## Exemple Numérique

```python
# Paramètres
N = 1000          # Population
eta = 21.6        # Constante universelle
beta = 0.92       # Exposant de diversité
lambda_inv = 0.7  # Taux d'investissement
kappa = 0.8       # Taux de couverture
rho = 0.5         # Taux de réinvestissement
price = 100.0     # Prix de référence

# 1. Production
fulus = eta * N * (N ** beta)  # = 12,376,800

# 2. Investissement
invest = lambda_inv * fulus    # = 8,663,760

# 3. Achat de commodités
quantity = invest / price       # = 86,637 unités

# 4. Émission de CBU
cbu = kappa * quantity * price  # = 6,930,992

# 5. Réinvestissement
reinvest = rho * cbu           # = 3,465,496
```

## Avantages du Mécanisme Purifié

1. **Stabilité physique** : Les CBU sont adossés à des stocks réels de commodités
2. **Transparence** : Le taux d'adossement est vérifiable on-chain
3. **Régulation automatique** : Le CRD stabilise les prix via floor/ceiling
4. **Croissance endogène** : La population croît grâce aux retours sur investissement
5. **Pas d'intérêt** : Le système repose sur le profit-sharing, pas sur le riba

## Références

- Youn, H., et al. (2014). "Urban economic diversity". *Nature*.
- Grondona, L. S. C. (1950-1982). Commodity Reserve Currency proposals.
- Daghar, M. (2026). CBU-X v2.0 Article. `docs/CBU-X_v2.0_Article.md`.
