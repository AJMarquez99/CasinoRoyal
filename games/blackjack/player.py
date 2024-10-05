import math

from typing import Optional, List, Tuple
from components import Symbol, Deck, Player, Card, Chip

from .utils import ace_total

class AI(Player):
    high_cards = [Symbol.TEN, Symbol.JACK, Symbol.QUEEN, Symbol.KING, Symbol.ACE]
    low_cards = [Symbol.TWO, Symbol.THREE, Symbol.FOUR, Symbol.FIVE, Symbol.SIX]

    def __init__(self, cash: int, name: Optional[str] = None):
        super().__init__(cash, name)
        
        self._card_memory: Deck = []
        self._running_count: int = 0
        self._true_count: float = 0
        self._safe_bankroll = 400
        self._table_min_bet: Optional[int] = None
        self._current_bet: Optional[int] = None

    @property
    def safe_bankroll(self) -> int:
        return self._safe_bankroll
    
    @safe_bankroll.setter
    def safe_bankroll(self, val: int):
        if val < 0:
            raise ValueError("Safe Bankroll value cannot be negative!")

        self._safe_bankroll = val

    def remember(self, cards: List[Deck]):
        all_cards = [card for deck in cards for card in deck]
        self._card_memory.extend(all_cards)

    def forget(self):
        self._card_memory.clear()
        self._running_count = 0
        self._true_count = 0
        self._current_bet = None
        self._table_min_bet = None
        
    def question(self, question: str, *args: str, **kwargs):
        available = [val.lower() for val in args]
        
        if question.find("bet") >= 0:
            min_bet = kwargs['min_bet']
            max_bet = kwargs['max_bet']
            
            return self._make_bet(min_bet)
        elif question.find("action") >= 0:
            try:
                cards = kwargs['cards']
                seat_number = kwargs['index']
                num_decks = kwargs['num_decks']

                return self._take_game_action(available, cards, seat_number, num_decks)
            except Exception as e:
                raise Exception(f"Player Take Action Exception: {e}")
            
    def _make_bet(self, min_bet: int) -> str:
        self._table_min_bet = min_bet
        self._manage_bankroll()

        if self._bankroll.total < min_bet:
            self.cash_out()
            return "l"

        risk = self._bankroll.total // min_bet
        favor = self._true_count

        if risk <= 4 or favor <= 1:
            self._current_bet = min_bet
            return str(min_bet)
        
        favor_bet = (favor - 1) * 2 * min_bet
        risk_bet = (min_bet * math.ceil(risk * 0.25))

        favor_bet = Chip.to_chip_int(favor_bet)
        risk_bet = Chip.to_chip_int(risk_bet)

        bet = str(max(min_bet, min(favor_bet, risk_bet)))
        self._current_bet = int(bet)

        return bet
        
    def _manage_bankroll(self):
        cash_out = 0
        clear = self._initial >= self._safe_bankroll

        if self.bankroll.count > 50:
            self.bankroll.optimize()

        # Cash Out Logic
        if self._cash >= self._initial:
            if clear and self._bankroll.total >= (self._cash // self._initial) * self._initial:
                cash_out = self._bankroll.divide(2).total
            elif not clear and self._bankroll.total >= ((self._cash // self._initial) + 1) * self._initial:
                cash_out = self._initial
        else:
            if clear and self._bankroll.total >= self._initial * 1.5:
                cash_out = self._initial
            elif self._bankroll.total >= self._initial * 3:
                cash_out = self._initial

        if cash_out > 0:
            self.cash_out(cash_out)

        # Buy In Logic
        if self._cash <= self._initial and self._bankroll.total < self._table_min_bet:
            bankroll_amt = self._cash // 2 if self._cash >= self._safe_bankroll else self._cash
            self.buy_in(bankroll_amt)

    def _take_game_action(self, options: List[str], cards: List[Deck], index: int, total_decks: int) -> str:
        original_deck_count = total_decks * 52

        player_hand = cards[index]

        player_total = ace_total(cards[index])
        dealer_total = ace_total(cards[-1])

        all_cards = [card for deck in cards for card in deck]
        all_cards.extend(self._card_memory)

        for card in all_cards:
            self._update_count(card)

        self._calculate_true_count(total_decks, len(all_cards))
        (high, low) = self._calculate_probabilities(all_cards, original_deck_count)

        if self._current_bet <= self._bankroll.total:
            if "t" in options:
                response = self._decide_split(player_hand[0].symbol.value, dealer_total)
                if response:
                    return response
            
            if "d" in options:
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
                # return "h" if self._true_count < 0 or dealer_total in [7, 8] else "s"

                return "r" if dealer_total >= 9 and "r" in options else "s" if dealer_total <= 6 else "h"
            case 15:
                return "r" if dealer_total == 10 and "r" in options else "h" if dealer_total >= 7 else "s"
            case 14 | 13:
                return "h" if dealer_total >= 7 else "s"
            case 12:
                return "s" if dealer_total in [4, 5, 6] else "h"
            case 11 | 10 | 9:
                return "h"
        
    def _decide_split(self, pair: int, dealer: int) -> Optional[str]:
        match pair:
            case 1 | 8:
                return "t"
            case 9:
                return "t" if  dealer <= 9 and dealer != 7 else None
            case 7:
                return "t" if dealer <= 7 else None
            case 6:
                return "t" if dealer <= 6 else None
            case 4:
                return "t" if dealer in [5, 6] else None
            case 3 | 2:
                return "t" if dealer <= 7 else None
            case _:
                return None

    def _decide_double_down(self, player: Deck, dealer: int) -> Optional[str]:
        ace = True if Symbol.ACE in [card.symbol for card in player] else False
        hand = player.total

        match hand:
            case 11:
                return "s" if ace else "d"
            case 10:
                return "s" if ace else "d" if dealer <= 9 else "h"
            case 9:
                return "s" if ace and dealer != 6 else "d" if 3 <= dealer <= 6 else "s"
            
        if ace:
            match hand:
                case 8:
                    return "d" if dealer <= 6 else "h" if dealer >= 9 else "s"
                case 7:
                    return "d" if 3 <= dealer <= 6 else "h"
                case 6 | 5:
                    return "d" if 4 <= dealer <= 6 else "h"
                case 4 | 3:
                    return "d" if dealer in [5, 6] else "h"
        return None
                
    def _calculate_true_count(self, total_decks: int, cards_played: int):
        decks_remaining = total_decks - (cards_played // 52)
        self._true_count = (self._running_count / decks_remaining) if decks_remaining > 0 else 0
    
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
 