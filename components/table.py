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
    
    @bet.setter
    def bet(self, bet: Pot):
        self._bet = bet
    
    @property
    def empty(self) -> bool:
        return self._player is None

    def sit(self, player: Player) -> bool:
        if self._player is None:
            self._player = player
            return True
        return False
    
    def leave(self) -> bool:
        if not self._bet:
            self._player = None
            return True
        print(f"There is a current bet, Player({self._player.name}) cannot leave.")
        return False

    def pay(self, amt: Pot):
        self._player.chips.append(amt)
        self.bet = Pot()

    def __repr__(self):
        return f"Seat(Player=None)" if self.player is None else f"Seat(Player={self.player.name})"

class Table(ABC):
    def __init__(self, min_bet: int, max_bet: int | None, limit: int = 6):
        self._min_bet = min_bet
        self._max_bet = max_bet
        self._seats: List[Seat] = [Seat() for _ in range(limit)]

    @property
    def min_bet(self) -> int:
        return self._min_bet
    
    @property
    def max_bet(self) -> Optional[int]:
        return self._max_bet
    
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
    
    def show_seats(self):
        print(self._seats)

    def show_players(self):
        print(self.players)
    
    def join(self, player: Player, index: Optional[int] = None) -> bool:
        if index is not None:
            if 0 <= index < len(self._seats) and self.get_player(index) is None:
                self._seats[index].sit(player)
                return True
            else:
                print(f"Table seat {index} is not available")
                return False
        else:
            for i, seat in enumerate(self._seats):
                if seat.player is None:
                    self._seats[i].sit(player)
                    return True
        print("Table is full")
        return False
        
    def leave(self, player: Player):
        for i, seat in enumerate(self._seats):
            if seat.player == player:
                self.seat.leave()
                return True
        print(f"{player} is not at this table")
        return False