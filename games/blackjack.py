import time

from typing import Optional, List, Tuple
from components import Table, Seat, Player, Deck, Card, Symbol, Pot
  
def ace_total(cards: Deck) -> int:
    total = cards.total
    if isinstance(cards.find(Symbol.ACE), int):
        alt_total = total + 10
        return alt_total if alt_total <= 21 else total
    return total

class BlackJackSeat(Seat):
    def __init__(self, player: Optional[Player] = None, is_split: bool = False):
        super().__init__(player)
        self._cards = Deck()
        self._action: Optional[str] = None
        self._insurance: Optional[Pot] = None
        self._is_split: bool = is_split

    @property
    def cards(self):
        return self._cards
    
    @property
    def action(self):
        return self._action
    
    @action.setter
    def action(self, val: str):
        self.action = val

    @property
    def insurance(self):
        return self.insurance
    
    @insurance.setter
    def insurance(self, val: Pot):
        self._insurance = val

    @property
    def is_split(self):
        return self._is_split
    
    def sit(self, player: Player) -> bool:
        self._deck = Deck()
        return super().sit(player)

    def leave(self) -> bool:
        if not self._deck:
            raise Exception(f"Player({self._player.name}) still has cards. Please discard them before leaving.")
        return super().leave()
    
    def pay_insurance(self):
        if self._insurance:
            self._player.chips.append(self._insurance.multiply(2))
            self._insurance = None
    
    def __repr__(self):
        return f"Seat(Empty)" if self.player is None else f"Seat(Player: {self.player.name}, Cards: {', '.join([card.name for card in self._cards])})"

class BlackJack(Table):
    def __init__(self, min_bet: int, max_bet: int | None = None, num_decks: int = 8, limit: int = 6, show: bool = False):
        super().__init__(min_bet, max_bet, limit)
        self._show = show
        self._num_decks = num_decks
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
    
    def reshuffle(self):
        self._deck.extend(self._discard)
        self._discard.clear()
        self._deck.shuffle()
    
    def play(self):
        if len(self.deck) < ((self._num_decks * 52) * (11/16)):
            self.reshuffle()
            self.narrate("Reshuffling deck...")

            for player in self.players:
                if isinstance(player, BlackJackAI):
                    player.forget()

        self._take_bets()
        self.narrate("Taking in bets...")

        if not self.seats_in_play:
            exit()

        self._deal()
        if self.show:
            time.sleep(2)

        for seat in self.seats_in_play:
            self._player_turn(seat)

        self._dealer_turn()
        if self.show:
            time.sleep(2)
            print()

        for player in self.players:
            if isinstance(player, BlackJackAI):
                player.remember(self._get_cards_in_play())

        self._pay_out()
        if self.show:
            print()
        
        if self.show:
            for seat in self.seats_with_players:
                print(seat.player)
                
            time.sleep(2)

        if self.show:
            print()
    
    def _take_bets(self) -> None:
        for seat in self.seats_with_players:
            while True:
                try:
                    response = seat.player.question(f"Player({seat.player.name}), how much would you like to bet?\n$ ", max_bet = self._max_bet, min_bet = self._min_bet)
                    if not response:
                        self.narrate(f"Player({seat.player.name}) is not playing this round.")
                        break

                    amt = int(response)
                    if self.min_bet <= amt <= (self.max_bet if self.max_bet is not None else amt):
                        seat.bet = seat.player.bet(amt)
                        break
                    else:
                        raise ValueError(f"Bet must be between {self.min_bet} and {self.max_bet or 'unlimited'}.")
                except Exception as e:
                    self.narrate(e)

    def _deal(self) -> None:
        for x in range(2):
            for seat in self.seats_in_play:
                seat.cards.append(self.draw())
                self.show(seat.player, seat.cards)
                #time.sleep(1)
            hide = True if x > 0 else False
            
            self.dealer.cards.append(self.draw())
            self.show(self.dealer.player, self.dealer.cards, hide)
            #time.sleep(1)
            #print()

    def _player_turn(self, seat: BlackJackSeat):
        initial = True
        insurance = True if self.dealer.cards[0].symbol is Symbol.ACE else False
        while ace_total(seat.cards) < 21:
            self.show(seat.player, seat.cards)
            try:
                index = self.seats_in_play.index(seat)
                cards = self._get_cards_in_play(True)

                if initial:
                    if len(cards[index]) > 1 and cards[index][0].symbol == cards[index][1].symbol:
                        if insurance:
                            response = seat.player.question(f"Player({seat.player.name}), take action. (H)it, (S)tand, (D)ouble Down, Spli(t), (I)nsurance, or Surrende(r)?\n", "h", "s", "d", "t", "r", "i", cards=cards, index=index, num_decks=self._num_decks, initial=initial)
                        else:
                            response = seat.player.question(f"Player({seat.player.name}), take action. (H)it, (S)tand, (D)ouble Down, Spli(t), or Surrende(r)?\n", "h", "s", "d", "t", "r", cards=cards, index=index, num_decks=self._num_decks, initial=initial)
                    elif insurance:
                        response = seat.player.question(f"Player({seat.player.name}), take action. (H)it, (S)tand, (D)ouble Down, Spli(t), or (I)nsurance?\n", "h", "s", "d", "r", "i", cards=cards, index=index, num_decks=self._num_decks, initial=initial)
                    else:
                        response = seat.player.question(f"Player({seat.player.name}), take action. (H)it, (S)tand, (D)ouble Down, or Surrende(r)?\n", "h", "s", "d", "r", cards=cards, index=index, num_decks=self._num_decks, initial=initial)
                else:
                    response = seat.player.question(f"Player({seat.player.name}), take action. (H)it or (S)tand?\n", "h", "s", cards=cards, index=index, num_decks=self._num_decks, initial=initial)

                if isinstance(seat.player, BlackJackAI):
                    self.narrate(f"AI Response: {response}")

                match response:
                    case "h": 
                        seat.cards.append(self.draw())
                        initial = False
                    case "s":
                        break
                    case "r":
                        seat.pay(seat.bet.divide(2))
                        break
                    case "d":
                        seat.bet.append(seat.player.bet(seat.bet.total))
                        seat.cards.append(self.draw())
                        break
                    case "t":
                        self._seats.insert(index+1, BlackJackSeat(seat.player, True))
                        self._seats[index+1].cards.append(seat.cards.pop())
                        self._seats[index+1].bet = seat.player.bet(seat.bet.total)
                        self._player_turn(self._seats[index+1])
                    case "i":
                        self._take_insurance_bet(seat)
                    case _:
                        raise ValueError(f"Invalid action '{response}'. Please enter 'H' for Hit or 'S' for Stand.")
            except Exception as e:
                self.narrate(e)
        
        self.show(seat.player, seat.cards)

        if ace_total(seat.cards) > 21:
            self.narrate(f"{seat.player.name} busted!")

    def _dealer_turn(self):
        self.show(self.dealer.player, self.dealer.cards)
        while ace_total(self.dealer.cards) < 17:
            # time.sleep(2)
            self.dealer.cards.append(self.draw())
            self.show(self.dealer.player, self.dealer.cards)

        self.show(self.dealer.player, self.dealer.cards)
        
        if ace_total(self.dealer.cards) > 21:
            self.narrate(f"Player({self.dealer.player.name}) busted!")

    def _pay_out(self):
        total = ace_total(self.dealer.cards)

        for seat in self.seats_with_players:
            if seat in self.seats_in_play:
                player_total = ace_total(seat.cards)
                black_jack = self._black_jack(seat.cards)
                self.discard.extend(seat.cards)
                seat.cards.clear()
                if player_total > 21 or (total <= 21 and player_total < total):
                    self.narrate(f"{seat.player.name}: Lost")
                elif total > 21 or player_total > total:
                    self.narrate(f"{seat.player.name}: Won")
                    seat.pay(seat.bet.multiply(2))
                    if black_jack:
                        seat.pay(seat.bet.divide(2))
                elif player_total == total:
                    self.narrate(f"{seat.player.name}: Push")
                    seat.pay(seat.bet)
                    if black_jack:
                        seat.pay(seat.bet.divide(2))

                if self.dealer.cards[0].symbol is Symbol.ACE and total == 21 and len(self.dealer.cards) == 2:
                    seat.pay_insurance()
            
            else:
                self.discard.extend(seat.cards)
                seat.cards.clear()

        self._remove_splits()

        self.discard.extend(self.dealer.cards)
        self.dealer.cards.clear()

    def _black_jack(self, cards: Deck) -> bool:
        if len(cards) == 2 and ace_total(cards) == 21:
            return True
        return False

    def _remove_splits(self):
        splits = []
        for index, seat in enumerate(self._seats):
            if seat.is_split:
                splits.insert(0, index)

        for index in splits:
            self._seats.pop(index)

    def _take_insurance_bet(self, seat: BlackJackSeat):
        max_bet = (seat.bet.total / 2)
        max_bet = max_bet + (5 - max_bet % 5)
        response = int(seat.player.question(f"How much would you like to place on insurance, up to ${seat.bet.total}?\n$ "))
        
        if response < max_bet:
            seat.insurance = seat.player.bet(int(response))
        else:
            raise ValueError("Insurance bet can only be up to half of your initial bet.")

    def _get_cards_in_play(self, dealer_hide = False) -> List[Deck]:
        table_state = []
        for seat in self.seats_in_play:
            table_state.append(seat.cards)

        if dealer_hide:
            table_state.append(Deck(self.dealer.cards[:-1]))
        else:
            table_state.append(self.dealer.cards)

        return table_state
    
    def narrate(self, statement: str):
        if self._show:
            print(statement)

    def show(self, player: Player, cards: Deck, hide_last: bool = False) -> None:
        if hide_last:
            self.narrate(f"Player({player.name}) has [{', '.join([card.name for card in cards[:-1]])}, ?]")
        else:
            self.narrate(f"Player({player.name}) has {cards.show(True)}")

class BlackJackAI(Player):
    high_cards = [Symbol.TEN, Symbol.JACK, Symbol.QUEEN, Symbol.KING, Symbol.ACE]
    low_cards = [Symbol.TWO, Symbol.THREE, Symbol.FOUR, Symbol.FIVE, Symbol.SIX]
    _card_memory: Deck = []
    _running_count: int = 0
    _true_count: float = 0

    def __init__(self, name: str, cash: int):
        super().__init__(name, cash)

    def remember(self, cards: List[Deck]):
        all_cards = [card for deck in cards for card in deck]
        self._card_memory.extend(all_cards)

    def forget(self):
        self._card_memory.clear()
        self._running_count = 0
        self._true_count = 0

    def question(self, question: str, *args: str, **kwargs):
        available = [val.lower() for val in args]
        
        if question.find("bet") >= 0:
            min_bet = kwargs['min_bet']
            max_bet = kwargs['max_bet']
            return self._make_bet(available, min_bet, max_bet)
        elif question.find("action") >= 0:
            cards = kwargs['cards']
            seat_number = kwargs['index']
            num_decks = kwargs['num_decks']
            initial = kwargs['initial']
            return self._take_action(available, cards, seat_number, num_decks, initial)
            
    def _make_bet(self, options: List[str], min_bet: int, max_bet: Optional[int]) -> str:
        total_value = self._cash + self._chips.total

        if self._true_count <= 1:
            return str(min_bet)
        elif 1 < self._true_count <= 2 and total_value > min_bet * 2:
            return str(min_bet * 2)
        elif 2 < self._true_count <= 3 and total_value > min_bet * 4:
            return str(min_bet * 4)
        elif total_value > min_bet * 8:
            return str(min_bet * 8)
        else:
            return str(min_bet)

    def _take_action(self, options: List[str], cards: List[Deck], index: int, total_decks: int, initial: bool) -> str:
        original_deck_count = total_decks * 52
        player_count = len(cards) - 1

        player_hand = cards[index]

        player_total = ace_total(cards[index])
        dealer_total = ace_total(cards[-1])

        all_cards = [card for deck in cards for card in deck]
        all_cards.extend(self._card_memory)

        for card in all_cards:
            self._update_count(card)

        self._calculate_true_count(total_decks, len(all_cards))
        (high, low) = self._calculate_probabilities(all_cards, original_deck_count)

        if len(player_hand) == 2 and initial and player_hand[0].symbol == player_hand[1].symbol:
            response = self._decide_split(player_hand[0].symbol.value, dealer_total)
            if response:
                return response
        
        if len(player_hand) == 2 and initial:
            response = self._decide_double_down(player_hand, dealer_total)
            if response:
                return response


        if player_total <= 8:
            return "h"
        elif player_total >= 17:
            # if player_hand.total == 7:
            #     return "h"
            return "s"
        
        match player_total:
            case 16:
                if dealer_total >= 9:
                    return "r"
                else:
                    return "h" if self._true_count < 0 or dealer_total in [7, 8] else "s"
            case 15:
                if dealer_total == 10:
                    return "r"
                else:
                    return "h" if self._true_count < 4 or dealer_total >= 7 else "s"
            case 14 | 13:
                return "s" if dealer_total <= 6 else "h"
            case 12:
                return "s" if dealer_total in [4, 5, 6] else "h"
            case 11 | 10:
                return "h"
            case 9:
                if dealer_total in [3, 4, 5, 6]:
                    return "h"
                else:
                    return "s" if low > 0.6 else "h"
                
        if self._true_count > 2:
            return "h" if high > 0.4 else "s"
        else:
            return "s" if low > 0.5 else "h"
        
    def _decide_split(self, pair: int, dealer: int) -> Optional[str]:
        match pair:
            case 1 | 8:
                return "t"
            case 9:
                return "t" if dealer != 7 and dealer <= 9 else "s"
            case 7:
                return "t" if dealer <= 7 else "h"
            case 2 | 3:
                return "t" if dealer <= 7 else "h"
            case 6:
                if dealer <= 6:
                    return "t"
            case 4:
                return "s"
            case _:
                return None

    def _decide_double_down(self, player: Deck, dealer: int) -> Optional[str]:
        hand = player.total
        ace = True if player[0].symbol is Symbol.ACE or player[1].symbol is Symbol.ACE else False
        match hand:
            case 11:
                return "s" if ace else "d"
            case 10:
                return "d" if dealer <= 9 else "h" if not ace else "s"
            case 9:
                if ace:
                    return "s" if dealer != 6 else "d"
                else:
                    return "d" if 3 <= dealer <= 6 else "h"
            case _:
                return None
    
    def _calculate_true_count(self, total_decks: int, cards_played: int):
        decks_remaining = total_decks - (cards_played / 52)
        self._true_count = self._running_count / decks_remaining if decks_remaining > 0 else 0
    
    def _update_count(self, card: Card):
        if card.symbol in self.low_cards:
            self._running_count += 1
        elif card.symbol in self.high_cards:
            self._running_count -= 1

    def _calculate_probabilities(self, all_cards: Deck, original_deck_count: int) -> Tuple[float]:
        cards_played = len(all_cards)
        
        high_card_count = sum(1 for card in all_cards if card.symbol in self.high_cards)
        low_card_count = sum(1 for card in all_cards if card.symbol in self.low_cards)

        total_high_cards = 4 * len(self.high_cards) * (original_deck_count // 52)
        total_low_cards = 4 * len(self.low_cards) * (original_deck_count // 52)

        remaining_cards = original_deck_count - cards_played

        return ((total_high_cards - high_card_count) / remaining_cards, (total_low_cards - low_card_count) / remaining_cards)
 