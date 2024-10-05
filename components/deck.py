from .utils import *
from typing import List, Optional, Union
import random    

class Card:
    __slot__ = ('suit', 'symbol', 'name', 'color')

    def __init__(self, symbol: Symbol, suit: Optional[Suit] = None) -> None:
        if symbol != Symbol.JOKER and suit is None:
            raise ValueError("Card must have suit unless card is Joker.")
        
        self.suit = suit
        self.symbol = symbol
        self.name = "Joker" if symbol is Symbol.JOKER else f"{symbol.name.capitalize()} of {suit.value}"
        self.color = None if symbol is Symbol.JOKER else get_card_color(suit)
    
    def __repr__(self):
        return f"Card({self.name})"

class Deck(List[Card]):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards or [])

    @property
    def total(self) -> int:
        return sum(card.symbol.value for card in self if card.symbol.value is not None)

    def shuffle(self) -> 'Deck':
        random.shuffle(self)
        return self
    
    def draw(self, qty: int = 1) -> Union[Card, 'Deck']:
        if not self:
            raise IndexError("Deck does not have any more cards to draw.")
        
        if qty == 1:
            return self.pop()
        
        return Deck([self.pop() for _ in range(qty)])
    
    def discard(self, index: Optional[int]) -> Card:
        return self.pop(index) if index is not None else self.pop()
    
    def discard_all(self) -> 'Deck':
        deck = Deck(self)
        self.clear
        return deck

    def peek(self) -> Optional[Card]:
        if not self:
            return None
        return self[-1]
    
    @staticmethod
    def create_standard_deck(qty: int = 1) -> 'Deck':
        deck = Deck()
        for _ in range(qty):
            deck.extend(Deck([Card(sym, suit) for suit in Suit for sym in Symbol if sym != Symbol.JOKER]))
        return deck

    def append(self, val: Union[Card, 'Deck']) -> 'Deck':
        if not isinstance(val, Card) |  isinstance(val, Deck):
            raise TypeError("Deck can only contain Card instances")
        
        if isinstance(val, Deck):
            self.extend(val)
        else:
            super().append(val)
        
        return self

    def extend(self, val: 'Deck') -> 'Deck':
        if isinstance(val, Deck):
            super().extend(val)
            return self

        raise TypeError("Deck can only be extended by a Deck")
        

    def __setitem__(self, index, value):
        if not isinstance(value, Card):
            raise TypeError("Deck can only contain Card instances")
        super().__setitem__(index, value)

    def __str__(self):
        return f"({', '.join([card.name for card in self])})"

    def __repr__(self):
        return f"Deck(length={len(self)}, cards=[{', '.join([card.name for card in self])}])"