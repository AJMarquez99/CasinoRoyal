from components import Symbol, Deck

def ace_total(cards: Deck) -> int:
    total = cards.total
    if sum(1 for card in cards if card.symbol is Symbol.ACE) > 0:
        alt_total = total + 10
        return alt_total if alt_total <= 21 else total
    return total