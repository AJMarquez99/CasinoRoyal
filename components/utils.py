from aenum import Enum, NoAlias

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    SPADES = "Spades"
    CLUBS = "Clubs"

class Symbol(Enum):
    _settings_ = NoAlias

    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 10
    QUEEN = 10
    KING = 10
    JOKER = None

class Color(Enum):
    BLACK = "Black"
    RED = "Red"
    GREEN = "Green"
    WHITE = "White"
    BLUE = "Blue"

def get_card_color(suit: Suit) -> Color:
    if suit in [Suit.CLUBS, Suit.SPADES]:
        return Color.BLACK
    elif suit in [Suit.DIAMONDS, Suit.HEARTS]:
        return Color.RED
    else:
        raise ValueError("Invalid Suit")
    
def bool_input(question: str, true: str = "y", false: str = "n") -> bool:
    action = input(question).lower()
    if action == true:
        return True
    elif action == false:
        return False
    else:
        raise ValueError(f"Invalid Input, must be '{true}' or '{false}'")