import time

from typing import Optional, List
from components import Table, Seat, Player, Deck, Card, Symbol, bool_input

class BlackJackSeat(Seat):
    def __init__(self, player: Optional[Player] = None):
        super().__init__(player)
        self._cards = Deck()

    @property
    def cards(self):
        return self._cards
    
    def sit(self, player: Player) -> bool:
        self._deck = Deck()
        return super().sit(player)

    def leave(self) -> bool:
        if not self._deck:
            raise Exception(f"Player({self._player.name}) still has cards. Please discard them before leaving.")
        return super().leave()
    
    def __repr__(self):
        return f"Seat(Empty)" if self.player is None else f"Seat(Player: {self.player.name}, Cards: {', '.join([card.name for card in self._cards])})"

class BlackJack(Table):
    def __init__(self, min_bet: int, max_bet: int | None = None, num_decks: int = 8, limit: int = 6):
        super().__init__(min_bet, max_bet, limit)
        self._deck = Deck.create_standard_deck(num_decks).shuffle()
        self._discard = Deck()
        self._dealer = BlackJackSeat(Player("Dealer", 0))
        self._seats: List[BlackJackSeat] = [BlackJackSeat() for _ in range(limit)]

    @property
    def deck(self) -> Deck:
        return self._deck
    
    @property
    def discard(self) -> Deck:
        return self._discard
    
    @property
    def dealer(self) -> BlackJackSeat:
        return self._dealer
    
    def draw(self) -> Card:
        return self.deck.draw()
    
    def _take_bets(self) -> None:
        for seat in self.seats_with_players:
            while True:
                try:
                    response = input(f"Player({seat.player.name}), how much would you like to bet?\n$ ")
                    # if not response:
                    #    break

                    amt = int(response)
                    if self.min_bet <= amt <= (self.max_bet if self.max_bet is not None else amt):
                        seat.bet = seat.player.bet(amt)
                        break
                    else:
                        print(f"Bet must be between {self.min_bet} and {self.max_bet or 'unlimited'}.")
                except Exception as e:
                    print(e)
    
    def play(self):
        self._take_bets()

        print("Taking in bets...")
        time.sleep(2)

        self._deal()
        time.sleep(2)

        for seat in self.seats_in_play:
            self._player_turn(seat)
            print()

        self._dealer_turn()
        time.sleep(3)
        print()

        self._pay_out()
        print()

        for seat in self.seats_with_players:
            print(seat.player)

        print()

    def _deal(self) -> None:
        for x in range(2):
            for seat in self.seats_in_play:
                seat.cards.append(self.draw())
                self.show(seat.player, seat.cards)
                time.sleep(1)
            hide = True if x > 0 else False
            
            self.dealer.cards.append(self.draw())
            self.show(self.dealer.player, self.dealer.cards, hide)
            time.sleep(1)
            print()

    def _player_turn(self, seat: BlackJackSeat):
        while self.total(seat.cards) < 21:
            self.show(seat.player, seat.cards)
            try:
                hit = bool_input(f"Player({seat.player.name}), (H)it or (S)tand?\n", "h", "s")
                if hit:
                    seat.cards.append(self.draw())
                else:
                    break
            except ValueError:
                print("Invalid action. Please enter 'H' for Hit or 'S' for Stand.")
        
        self.show(seat.player, seat.cards)

        if self.total(seat.cards) > 21:
            print(f"{seat.player.name} busted!")

    def _dealer_turn(self):
        self.show(self.dealer.player, self.dealer.cards)
        while self.total(self.dealer.cards) < 17:
            time.sleep(2)
            self.dealer.cards.append(self.draw())
            self.show(self.dealer.player, self.dealer.cards)

        self.show(self.dealer.player, self.dealer.cards)
        
        if self.total(self.dealer.cards) > 21:
            print(f"Player({self.dealer.player.name}) busted!")

    def _pay_out(self):
        total = self.total(self.dealer.cards)

        for seat in self.seats_in_play:
            player_total = self.total(seat.cards)
            self.discard.extend(seat.cards)
            seat.cards.clear()
            if player_total > 21 or (total <= 21 and player_total < total):
                print(f"{seat.player.name}: Lost")
            elif total > 21 or player_total > total:
                print(f"{seat.player.name}: Won")
                seat.pay(seat.bet.multiply(2))
            elif player_total == total:
                print(f"{seat.player.name}: Push")
                seat.pay(seat.bet)

        self.discard.extend(self.dealer.cards)
        self.dealer.cards.clear()

    @staticmethod
    def _parse_input(question: str, *args: str) -> str:
        response = input(question).lower()
        available = [val.lower() for val in args]
        if response in available:
            return response
        raise ValueError("Invalid user input")

    @staticmethod
    def total(cards: Deck) -> int:
        total = cards.total
        if isinstance(cards.find(Symbol.ACE), int):
            alt_total = total + 10
            return alt_total if alt_total <= 21 else total
        return total

    @staticmethod
    def show(player: Player, cards: Deck, hide_last: bool = False) -> None:
        if hide_last:
            print(f"Player({player.name}) has [{', '.join([card.name for card in cards[:-1]])}, ?]")
        else:
            print(f"Player({player.name}) has {cards.show(True)}")