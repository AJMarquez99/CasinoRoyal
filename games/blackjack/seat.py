from typing import Optional
from components import Seat, Player, Deck, Pot

class BlackJackSeat(Seat):
    def __init__(self, player: Optional[Player] = None):
        super().__init__(player)
        self._cards = Deck()

    @property
    def cards(self):
        return self._cards

    def leave(self) -> bool:
        if len(self._cards) > 0:
            raise Exception(f"Player({self._player.name}) still has cards. Please discard them before leaving.")
        return super().leave()
    
    def __repr__(self):
        return f"Seat(Empty)" if self.player is None else f"Seat(Player: {self.player.name}, Cards: {', '.join([card.name for card in self._cards])})"