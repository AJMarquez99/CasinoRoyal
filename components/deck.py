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
    
    def draw(self, qty: int = 1) -> Union[Card, 'Deck', None]:
        if not self:
            return None
        if qty == 1:
            return self.pop()
        return Deck([self.pop() for _ in range(min(qty, len(self)))])
    
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
    
    def show(self, as_string = False) -> Optional[str]:
        if as_string:
            return f"[{', '.join([card.name for card in self])}]"
        else:
            print(f"[{', '.join([card.name for card in self])}]")

    def find(self, val: Union[Symbol, Suit]) -> Optional[int]:
        if isinstance(val, Symbol):
            for x, card in enumerate(self):
                temp = "True" if card.symbol == val else "False"
                if card.symbol == val:
                    return x
            return None
        if isinstance(val, Suit):
            for x, card in enumerate(self):
                if card.suit == val:
                    return x
            return None
        raise ValueError("Deck search can only take a Suit or Symbol")
    
    def is_full_deck(self) -> bool:
        return len(self) % 52 == 0
    
    @staticmethod
    def create_standard_deck(qty: int = 1) -> 'Deck':
        deck = Deck()
        for _ in range(qty):
            deck.extend([Card(sym, suit) for suit in Suit for sym in Symbol if sym != Symbol.JOKER])
        return deck

    def append(self, value: any) -> None:
        if not isinstance(value, Card) |  isinstance(value, List):
            raise TypeError("Deck can only contain Card instances")
        if isinstance(value, List):
            self.extend(value)
        else:
            super().append(value)

    def extend(self, values: List) -> None:
        if not all(isinstance(card, Card) for card in values):
            raise TypeError("Deck can only contain Card instances")
        super().extend(values)

    def __setitem__(self, index, value):
        if not isinstance(value, Card):
            raise TypeError("Deck can only contain Card instances")
        super().__setitem__(index, value)

    def __repr__(self):
        return f"Deck(cards={len(self)})"