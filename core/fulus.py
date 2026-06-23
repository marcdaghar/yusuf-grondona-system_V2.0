"""
Module de gestion des fulus (monnaie de vélocité)
Émission et destruction, demurrage (décroissance programmée)

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FulusWallet:
    """Portefeuille de fulus"""
    address: str
    balance: float
    last_activity: float  # timestamp


class FulusSystem:
    """
    Système de gestion des fulus (monnaie de vélocité)

    Caractéristiques:
    - Pas d'intérêt
    - Demurrage (décroissance programmée)
    - Émission contre nuqud
    """

    def __init__(self, demurrage_rate: float = 0.025):
        """
        Args:
            demurrage_rate: Taux de décroissance annuel (défaut 2.5%)
        """
        self.wallets: Dict[str, FulusWallet] = {}
        self.total_supply: float = 0.0
        self.demurrage_rate = demurrage_rate

    def create_wallet(self, address: str, initial_balance: float = 0.0) -> FulusWallet:
        """Crée un portefeuille fulus"""
        wallet = FulusWallet(
            address=address,
            balance=initial_balance,
            last_activity=0.0
        )
        self.wallets[address] = wallet
        self.total_supply += initial_balance
        return wallet

    def issue_fulus(self, address: str, amount: float, 
                   against_nuqud_value: float = 0.0) -> bool:
        """Émet des fulus contre une valeur en nuqud"""
        if address not in self.wallets:
            return False

        if against_nuqud_value >= amount:
            self.wallets[address].balance += amount
            self.total_supply += amount
            return True
        return False

    def transfer(self, from_addr: str, to_addr: str, amount: float) -> bool:
        """Transfère des fulus d'un portefeuille à l'autre"""
        if from_addr not in self.wallets or to_addr not in self.wallets:
            return False

        self.apply_demurrage(from_addr)

        if self.wallets[from_addr].balance < amount:
            return False

        self.wallets[from_addr].balance -= amount
        self.wallets[to_addr].balance += amount

        current_time = 0.0
        self.wallets[from_addr].last_activity = current_time
        self.wallets[to_addr].last_activity = current_time

        return True

    def apply_demurrage(self, address: str) -> float:
        """Applique le demurrage à un portefeuille"""
        if address not in self.wallets:
            return 0.0

        wallet = self.wallets[address]
        time_elapsed = 1.0

        decay = wallet.balance * self.demurrage_rate * time_elapsed
        if decay > 0:
            wallet.balance = max(0, wallet.balance - decay)
            self.total_supply -= decay

        return decay

    def apply_demurrage_all(self) -> Dict[str, float]:
        """Applique le demurrage à tous les portefeuilles"""
        decays = {}
        for address in list(self.wallets.keys()):
            decays[address] = self.apply_demurrage(address)
        return decays

    def get_velocity(self, total_transactions: float, period: float = 1.0) -> float:
        """
        Calcule la vélocité des fulus
        V = (P * T) / M
        """
        if self.total_supply == 0:
            return 0.0
        return total_transactions / self.total_supply / period
