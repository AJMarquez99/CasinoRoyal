import time

from abc import ABC, abstractmethod
from typing import Union, Optional, List

from .pot import Pot
from .player import Player

class Seat:
    def __init__(self, player: Optional[Player] = None):
        self._player = player
        self._bet = Pot()

    @property
    def player(self) -> Optional[Player]:
        return self._player
    
    @property
    def bet(self) -> Pot:
        return self._bet
    
    @property
    def empty(self) -> bool:
        return self._player is None

    def sit(self, player: Player) -> bool:
        if self._player is None:
            self._player = player
        else:
            raise AttributeError(f"This seat is take by {str(self._player)}.")
    
    def leave(self):
        if not self._bet:
            self._player = None
        else:
            raise AttributeError(f"There is a current bet, {str(self._player)} cannot leave.")
    
    def make_bet(self, bet: Union[int, Pot]):
        self._bet = self._player.bet(bet)

    def pay(self, amt: Union[int, Pot]):
        self._player.pay(amt)

        self._bet.clear()

    def __repr__(self):
        return f"Seat(Player=None)" if self.player is None else f"Seat(Player={self.player.name}, Bet Amount={self._bet})"

class Table(ABC):
    def __init__(self, min_bet: int = 0, max_bet: int | None = None, limit: int = 6):
        self._min_bet = min_bet
        self._max_bet = max_bet
        self._seats: List[Seat] = [Seat() for _ in range(limit)]
        self._player_limit = limit

    @property
    def min_bet(self) -> int:
        return self._min_bet
    
    @property
    def max_bet(self) -> Optional[int]:
        return self._max_bet
    
    @property
    def player_limit(self) -> int:
        return self._player_limit
    
    @property
    def seats(self) -> List[Seat]:
        return self._seats
    
    @property
    def seats_with_players(self) -> List[Seat]:
        return [seat for seat in self._seats if seat.player is not None]
    
    @property
    def seats_in_play(self) -> List[Seat]:
        return [seat for seat in self.seats_with_players if seat.bet]
    
    @property
    def players(self):
        return [seat.player for seat in self.seats_with_players]
    
    def get_player(self, index: int) -> Optional[Player]:
        return self._seats[index].player
    
    def find_player(self, player: Player) -> Seat:
        for seat in self._seats:
            if seat.player == player:
                return seat
        raise ValueError(f"{player} is not at this table!")
    
    def join(self, player: Player, index: Optional[int] = None):
        if index is not None:
            try:
                if 0 <= index < len(self._seats):
                    self._seats[index].sit(player)
            except Exception as e:
                raise IndexError(f"Table seat {index} is not available. {e}")
        else:
            sat = False
            for i, seat in enumerate(self._seats):
                if seat.player is None:
                    seat.sit(player)
                    sat = True
                    break
            if not sat:
                raise IndexError("Table is full!")
        
    def leave(self, player: Player):
        self.find_player(player).leave()