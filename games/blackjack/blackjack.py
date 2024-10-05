import time

from typing import List, Dict
from components import Table, Player, Deck, Card, Symbol, Pot, Suit

from .seat import BlackJackSeat
from .player import AI
from .utils import ace_total

class BlackJack(Table):
    def __init__(self, min_bet: int, max_bet: int | None = None, num_decks: int = 8, limit: int = 6, narrate: bool = False, narrate_speed: int = 1):
        super().__init__(min_bet, max_bet, limit)
        self._seats: List[BlackJackSeat] = [BlackJackSeat() for _ in range(limit)]
        self._insurance: Dict[Player, Pot] = {}

        self._deck = Deck.create_standard_deck(num_decks).shuffle()
        self._discard = Deck()
        self._num_decks = num_decks
        self._cut_card = num_decks * 52 * (11/16)

        self._dealer = BlackJackSeat(Player(0, "Dealer"))
        self._narrate = narrate
        self._narrate_speed = narrate_speed if narrate else 0
        self._splits = False
    
    @property
    def seats_in_play(self) -> List[BlackJackSeat]:
        return [seat for seat in self.seats_with_players if seat.bet]

    def draw(self) -> Card:
        return self._deck.draw()
    
    def reshuffle(self):
        self._deck.extend(self._discard)
        self._discard.clear()
        self._deck.shuffle()
    
    def play(self):
        if len(self._deck) < self._cut_card:
            self.reshuffle()
            self.narrate("Reshuffling deck...")

            for player in self.players:
                if isinstance(player, AI):
                    self.narrate(f"AI {player} is forgetting current counts...")
                    player.forget()

        self._take_bets()

        if not self.seats_in_play:
            self.narrate("\nNo players, game over!")
            return False

        self.narrate("\nLocking bets in...\n")
        time.sleep(self._narrate_speed)

        self._deal()
        time.sleep(self._narrate_speed)

        for seat in self.seats_in_play:
            self._player_turn(seat)

        self._dealer_turn()
        time.sleep(self._narrate_speed)

        for player in self.players:
            if isinstance(player, AI):
                player.remember(self._get_cards_in_play())

        self._pay_out()
        
        for seat in self.seats_with_players:
            self.narrate(repr(seat.player))

        self.narrate("\n")
                
        time.sleep(self._narrate_speed * 3)
    
    def _take_bets(self) -> None:
        for seat in self.seats_with_players:
            tries = 0
            while True:
                try:
                    response = seat.player.question(f"Player({seat.player.name}), how much would you like to bet?\n$ ", max_bet = self._max_bet, min_bet = self._min_bet)
                    if not response:
                        self.narrate(f"Player({seat.player.name}) is not playing this round.\n")
                        break

                    if response == "l":
                        player = seat.player
                        seat.leave()
                        self.narrate(f"\nPlayer({player.name}) has left the table.\n")
                        break

                    amt = int(response)

                    if isinstance(seat.player, AI):
                        self.narrate(f"Player({seat.player.name}), how much would you like to bet?\n$ {response}")
                        time.sleep(self._narrate_speed / 2)

                    if self.min_bet <= amt <= (self.max_bet if self.max_bet is not None else amt):
                        seat.make_bet(amt)
                        break
                    else:
                        raise ValueError(f"Bet must be between {self.min_bet} and {self.max_bet or 'unlimited'}.")
                except Exception as e:
                    if tries > 3:
                        raise Exception(f"Taking Bets Exception: {e}")
                    else:
                        self.narrate(e)
                        tries += 1

    def _deal(self) -> None:
        for x in range(2):
            for seat in self.seats_in_play:
                seat.cards.append(self.draw())
                self.narrate(repr(seat))
                time.sleep(self._narrate_speed/2)

            self._dealer.cards.append(self.draw())

            if x > 0:
                self.initial_dealer_show()
            else:
                self.narrate(f"{repr(self._dealer)}\n")

            time.sleep(self._narrate_speed/2)

        #self._dealer.cards.clear()
        #self._dealer.cards.append(Deck([Card(Symbol.ACE, Suit.CLUBS), Card(Symbol.TEN, Suit.CLUBS)]))

        if self._dealer.cards[0].symbol is Symbol.ACE:
            self._take_insurance()

    def _take_insurance(self):
        for seat in self.seats_in_play:
            q_tries = 0
            while True:
                try:
                    response = seat.player.question(f"Would you like to take insurance? (Y/N)\n", "y", "n")

                    if response == "y":
                        tries = 0
                        while True:
                            try:
                                limit = seat.bet.total // 2
                                limit = limit - (limit % 5)
                                insurance = seat.player.question(f"How much insurance would you like to take? Your limit is ${limit}:\n")

                                if not insurance:
                                    break
                                
                                insurance = int(insurance)
                                if insurance <= seat.bet.total // 2:
                                    self._insurance[seat.player] = seat.player.bet(insurance)
                                    break
                                else:
                                    raise ValueError("Insurance must be less than or equal to half your original bet!")
                            except Exception as e:
                                if tries > 2:
                                    break
                                self.narrate(f"Error taking insurance: {e}\n")

                    break
                except:
                    if q_tries > 1:
                        break

    def _pay_insurance(self):
        for player, insurance in self._insurance.items():
            player.pay(insurance.multiply(2))

        self._insurance.clear()

    def _player_turn(self, seat: BlackJackSeat):
        initial = True
        tries = 0

        self.narrate(f"\n{repr(seat)}")
        while ace_total(seat.cards) < 21:
            try:
                index = self.seats_in_play.index(seat)
                
                response = self._get_player_action(seat, initial, index)

                if isinstance(seat.player, AI):
                    self.narrate(f"AI Response: {response}")
                    time.sleep(self._narrate_speed / 2)

                self._handle_player_action(seat, response, index)

                if response in ['s', 'r', 'd']:
                    break

                initial = False
            except Exception as e:
                if tries > 3:
                    self.narrate(f"\nPlayer Turn Exception: {e} \nCurrent State:\nCards: {len(self._deck)}\nCurrent Seat: {repr(seat)}\nSeat Index:{index}\nSeats State:")

                    for table_seats in self._seats:
                        self.narrate(repr(table_seats))
                    break
                else:
                    self.narrate(f"Something went wrong. Please enter your option again.")
                    tries += 1

        if ace_total(seat.cards) > 21:
            self.narrate(f"\n{repr(seat)}\n{seat.player} busted!")

    def _get_player_action(self, seat: BlackJackSeat, initial: bool, index: int) -> str:
        options = {'h': "(H)it", 's': "(S)tand"}

        if self._can_split(seat.cards):
                options["t"] = "Spli(t)"

        if initial:
            options.update({'d': "(D)ouble Down", 'r': "Surrende(r)"})            
        
        options_string = ", ".join(list(options.values())[:-1])
        question = f"{seat.player}, take action. {options_string}, or {list(options.values())[-1]}?\n"

        return seat.player.question(question, *list(options.keys()), cards=self._get_cards_in_play(True), index=index, num_decks=self._num_decks)
    
    def _handle_player_action(self, seat: BlackJackSeat, response: str, index: int):
        match response:
            case "h":
                seat.cards.append(self.draw())
                self.narrate(f"\n{repr(seat)}")
            case "r":
                seat.pay(seat.bet.divide(2))
            case "d":
                seat.bet.append(seat.player.bet(seat.bet.total))
                seat.cards.append(self.draw())
                
                self.narrate(f"\n{repr(seat)}")
            case "t":
                self._handle_split(seat, index)
                
                self.narrate(f"\n{repr(seat)}")
            case _:
                if response != "s":
                    raise ValueError(f"Invalid action '{response}'. Please select one of the options mentioned previously.")
                
    def _handle_split(self, seat: BlackJackSeat, index: int):
        new_seat = BlackJackSeat(seat.player)
        new_seat.cards.append(seat.cards.pop())
        new_seat.make_bet(seat.bet.total)

        self._seats.insert(index + 1, new_seat)
        self._player_turn(new_seat)
        self._splits = True

    def _dealer_turn(self):
        self.narrate(f"\n{repr(self._dealer)}")

        while ace_total(self._dealer.cards) < 17:
            time.sleep(self._narrate_speed)
            self._dealer.cards.append(self.draw())
            self.narrate(repr(self._dealer))

        time.sleep(self._narrate_speed / 2)
        
        if ace_total(self._dealer.cards) > 21:
            self.narrate("Dealer busted!")

    def _pay_out(self):
        total = ace_total(self._dealer.cards)
        self.narrate("\n")

        for seat in self.seats_with_players:
            if seat in self.seats_in_play:
                player_total = ace_total(seat.cards)
                amount = 0

                if player_total > 21 or (total <= 21 and player_total < total):
                    self.narrate(f"{seat.player}: Lost")

                elif total > 21 or player_total > total:
                    self.narrate(f"{seat.player}: Won")
                    amount = seat.bet.multiply(2)

                    if self._black_jack(seat.cards):
                        amount.append(seat.bet.divide(2))

                elif player_total == total:
                    self.narrate(f"{seat.player}: Push")
                    amount = seat.bet

                    if self._black_jack(seat.cards) and not self._black_jack(self._dealer.cards):
                        amount.append(seat.bet.divide(2))

                seat.pay(amount)
            
            self._discard.extend(seat.cards)
            seat.cards.clear()

        if self._splits:
            self._remove_splits()

        if self._black_jack(self._dealer.cards) and self._dealer.cards[0].symbol is Symbol.ACE:
            self._pay_insurance()

        self._discard.extend(self._dealer.cards)
        self._dealer.cards.clear()
        self.narrate("\n")

    def _black_jack(self, cards: Deck) -> bool:
        if len(cards) == 2 and ace_total(cards) == 21:
            return True
        return False

    def _remove_splits(self):
        players = set()
        for index, seat in enumerate(self._seats):
            if seat.player in players:
                del self._seats[index]
            else:
                players.add(seat.player)

    def _get_cards_in_play(self, initial = False) -> List[Deck]:
        table_state = []
        for seat in self.seats_in_play:
            table_state.append(seat.cards)

        if initial:
            table_state.append(Deck(self._dealer.cards[:-1]))
        else:
            table_state.append(self._dealer.cards)

        return table_state
    
    @staticmethod
    def _can_split(cards: Deck) -> bool:
        if len(cards) == 2 and cards[0].symbol == cards[1].symbol:
            return True
        return False
    
    def narrate(self, statement: str):
        if self._narrate:
            print(statement)

    def initial_dealer_show(self) -> None:
        if self._narrate:
            print(f"Seat(Player: Dealer, Cards: {self._dealer.cards[0].name}, ?)")