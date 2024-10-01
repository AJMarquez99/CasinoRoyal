from typing import Optional
from .pot import Pot

class Player():
    def __init__(self, name: str, cash: int):
        self._name = name
        self._cash = cash
        self._chips = Pot()
        self._starting_cash = self._cash

    @property
    def name(self):
        return self._name

    @property
    def cash(self):
        return self._cash

    @property
    def chips(self):
        return self._chips

    def bet(self, amount: int) -> Pot:
        return self._chips.remove(amount)

    def buy_in(self, amount: int, ask: Optional[Pot] = None):
        if amount > self._cash:
            raise ValueError("A player cannot cash in more than is in their wallet")
        self._chips += Pot.buy_in(amount, ask)
        self._cash -= amount
    
    def cash_out(self):
        self._cash += self._pot.totalValue
        self._chips.clear()

    def question(self, question: str, *args: str, **kwargs) -> str:
        response = input(question).lower()

        if args:
            available = [val.lower() for val in args]

            if response in available:
                return response
            raise ValueError("Invalid Input")
        
        return response

    def __repr__(self):
        return f"Player(name={self._name}, cash={self._cash}, chips={self._chips})"