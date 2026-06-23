"""
Module du système Grondona (Commodity Reserve Department)
Gestion des prix plancher/plafond et des stockpiles
Mécanisme purifié: Guildes → Fulus → CRD → CBU

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import time


@dataclass
class Commodity:
    """Matière première dans le panier CBU"""
    name: str
    floor_price: float
    ceiling_price: float
    current_price: float
    stock: float
    elasticity: float = 1.0
    storage_cost: float = 0.005


@dataclass
class GuildInvestment:
    """Investissement d'une guilde dans le CRD"""
    guild_id: str
    commodity: str
    quantity: float
    price: float
    cbu_issued: float
    timestamp: float


class GrondonaCRD:
    """
    Commodity Reserve Department — Mécanisme purifié

    Flux économique:
    1. Guildes produisent des Fulus
    2. Guildes investissent Fulus → CRD
    3. CRD achète commodités, constitue stocks
    4. CRD émet des CBU adossés (80% couverture)
    5. CBU retournent aux guildes pour commerce
    6. Cycle vertueux (50% réinvesti)

    Mécanisme de régulation:
    - Prix < plancher: achat (expansion monétaire)
    - Prix > plafond: vente (contraction monétaire)
    """

    def __init__(self, coverage_rate: float = 0.8):
        self.commodities: Dict[str, Commodity] = {}
        self.money_supply: float = 0.0
        self.cbu_supply: float = 0.0
        self.investments: Dict[str, GuildInvestment] = {}
        self.investment_history: List[GuildInvestment] = []
        self.coverage_rate = coverage_rate
        self.history: List[Dict] = []

    def add_commodity(self, 
                      name: str,
                      floor_price: float,
                      ceiling_price: float,
                      initial_price: float,
                      initial_stock: float = 0.0,
                      elasticity: float = 1.0) -> None:
        """Ajoute une matière première au CRD"""
        self.commodities[name] = Commodity(
            name=name,
            floor_price=floor_price,
            ceiling_price=ceiling_price,
            current_price=initial_price,
            stock=initial_stock,
            elasticity=elasticity
        )

    def invest_fulus(self, guild_id: str, amount: float, commodity: str) -> bool:
        """
        Les guildes investissent leurs fulus dans le CRD

        Args:
            guild_id: Identifiant de la guilde
            amount: Montant en Fulus
            commodity: Type de commodité à acheter

        Returns:
            True si l'investissement réussit
        """
        if commodity not in self.commodities:
            return False

        if amount <= 0:
            return False

        # Achat de commodités avec les fulus
        price = self.commodities[commodity].current_price
        quantity = amount / price

        # Constitution des stocks physiques
        self.commodities[commodity].stock += quantity

        # Émission de CBU adossés (taux de couverture)
        cbu_issued = quantity * price * self.coverage_rate
        self.cbu_supply += cbu_issued
        self.money_supply += cbu_issued

        # Enregistrement de l'investissement
        investment = GuildInvestment(
            guild_id=guild_id,
            commodity=commodity,
            quantity=quantity,
            price=price,
            cbu_issued=cbu_issued,
            timestamp=time.time()
        )

        self.investments[guild_id] = investment
        self.investment_history.append(investment)

        return True

    def get_investment_return(self, guild_id: str) -> float:
        """
        Retour sur investissement pour une guilde

        Returns:
            Plus-value en pourcentage
        """
        if guild_id not in self.investments:
            return 0.0

        invest = self.investments[guild_id]
        commodity = self.commodities[invest.commodity]

        # Plus-value sur le stock
        current_value = invest.quantity * commodity.current_price
        initial_value = invest.quantity * invest.price

        if initial_value == 0:
            return 0.0

        return (current_value - initial_value) / initial_value

    def get_total_investments(self) -> Dict[str, float]:
        """Total des investissements par commodité"""
        totals = {}
        for inv in self.investment_history:
            totals[inv.commodity] = totals.get(inv.commodity, 0) + inv.cbu_issued
        return totals

    def step(self, market_prices: Dict[str, float]) -> Dict[str, Dict]:
        """
        Effectue une itération du système Grondona

        Returns:
            Dictionnaire des actions effectuées
        """
        actions = {}

        for name, price in market_prices.items():
            if name not in self.commodities:
                continue

            commodity = self.commodities[name]
            action = {
                'name': name,
                'action': 'none',
                'quantity': 0.0,
                'price': price,
                'money_flow': 0.0,
                'new_stock': commodity.stock
            }

            if price < commodity.floor_price:
                # Achat : expansion monétaire
                purchase_qty = (commodity.floor_price - price) * commodity.elasticity
                commodity.stock += purchase_qty
                self.money_supply += purchase_qty * commodity.floor_price

                action['action'] = 'buy'
                action['quantity'] = purchase_qty
                action['money_flow'] = purchase_qty * commodity.floor_price
                action['new_stock'] = commodity.stock

            elif price > commodity.ceiling_price:
                # Vente : contraction monétaire
                sale_qty = min(
                    commodity.stock,
                    (price - commodity.ceiling_price) * commodity.elasticity
                )
                commodity.stock -= sale_qty
                self.money_supply -= sale_qty * commodity.ceiling_price

                action['action'] = 'sell'
                action['quantity'] = sale_qty
                action['money_flow'] = -sale_qty * commodity.ceiling_price
                action['new_stock'] = commodity.stock

            commodity.current_price = price

            # Appliquer les coûts de stockage
            commodity.stock *= (1 - commodity.storage_cost)

            actions[name] = action

        self._log_state(actions)

        return actions

    def _log_state(self, actions: Dict) -> None:
        """Enregistre l'état du CRD"""
        state = {
            'money_supply': self.money_supply,
            'cbu_supply': self.cbu_supply,
            'total_investments': len(self.investment_history),
            'commodities': {
                name: {
                    'stock': c.stock,
                    'price': c.current_price,
                    'floor': c.floor_price,
                    'ceiling': c.ceiling_price
                }
                for name, c in self.commodities.items()
            },
            'actions': actions
        }
        self.history.append(state)

    def total_stock_value(self) -> float:
        """Calcule la valeur totale des stockpiles"""
        total = 0.0
        for c in self.commodities.values():
            total += c.stock * c.current_price
        return total

    def get_backing_ratio(self) -> float:
        """
        Taux d'adossement: valeur physique / CBU émis
        """
        if self.cbu_supply == 0:
            return 1.0
        return self.total_stock_value() / self.cbu_supply

    def get_entropy_bound(self) -> float:
        """Calcule la borne d'entropie du système"""
        total_value = self.total_stock_value()
        if total_value == 0:
            return 0.0

        shares = [c.stock * c.current_price / total_value for c in self.commodities.values()]
        shares = [s for s in shares if s > 0]

        if not shares:
            return 0.0

        return -np.sum(shares * np.log(shares))


def simulate_crd(initial_prices: Dict[str, float],
                 price_volatility: float = 0.15,
                 periods: int = 100,
                 floor_ratio: float = 0.8,
                 ceiling_ratio: float = 1.2) -> List[Dict]:
    """
    Simule le système Grondona sur une période donnée
    """
    crd = GrondonaCRD()

    for name, price in initial_prices.items():
        crd.add_commodity(
            name=name,
            floor_price=price * floor_ratio,
            ceiling_price=price * ceiling_ratio,
            initial_price=price,
            initial_stock=100.0
        )

    results = []
    for period in range(periods):
        market_prices = {}
        for name, c in crd.commodities.items():
            shock = 1 + np.random.normal(0, price_volatility)
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])

        actions = crd.step(market_prices)
        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'cbu_supply': crd.cbu_supply,
            'total_value': crd.total_stock_value(),
            'backing_ratio': crd.get_backing_ratio(),
            'actions': actions
        })

    return results
