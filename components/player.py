from typing import Optional, Union
from .pot import Pot
from .chip import Chip

class Player():
    __player_count = 0

    def __init__(self, cash: int, name: Optional[str] = None):
        if not name:
            Player.__player_count += 1
        
        self._name = name.capitalize() if name else f"Player{self.__player_count}"
        self._cash = cash
        self._bankroll = Pot()
        self._initial = self._cash

    @property
    def name(self):
        return self._name

    @property
    def cash(self):
        return self._cash

    @property
    def bankroll(self):
        return self._bankroll

    def bet(self, amount: Union[int, Pot]) -> Pot:
        return self._bankroll.remove(amount)
    
    def pay(self, amount: Union[int, Pot]) -> Pot:
        self._bankroll.append(amount)

        if isinstance(amount, int):
            return Pot.from_int(amount)
        
        return amount

    def buy_in(self, amount: Optional[int] = None, ask: Optional[Pot] = None):
        if not amount:
            self._bankroll += Pot.buy_in(self._cash)
            self._cash = 0
            return

        amount = amount if amount % Chip.min_value() == 0 else amount - (amount // Chip.min_value())

        if amount < 0:
            raise ValueError(f"A player cannot buy in for less than ${Chip.min_value()}!")
        
        if amount > self._cash:
            raise ValueError("A player cannot buy in more than is in their wallet!")
        
        self._bankroll += Pot.buy_in(amount, ask)
        self._cash -= amount
    
    def cash_out(self, chips: Optional[Pot | int] = None):
        if chips:
            if isinstance(chips, int):
                chips = chips if chips % Chip.min_value() == 0 else chips - (chips // Chip.min_value())
                
            self._cash += self._bankroll.remove(chips).total
        else:
            self._cash += self._bankroll.total
            self._bankroll.clear()

    def question(self, question: str, *args: str, **kwargs) -> str:
        response = input(question).lower()

        if args:
            available = [val.lower() for val in args]

            if response in available:
                return response
            
            raise ValueError("Invalid player response!")
        
        return response
    
    def __str__(self):
        return f"Player({self.name})"

    def __repr__(self):
        return f"Player(name={self._name}, cash=${self._cash}.00, bankroll={repr(self._bankroll)})"