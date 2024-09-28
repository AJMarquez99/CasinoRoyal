from components import *
import time

def main():
    print("TESTING:")
    
    blackjack = BlackJackTable(25)

    player1 = Player("Alejandro", 500)
    player2 = Player("Adam", 500)
    player3 = Player("Janaea", 500)

    player1.buy_in(500, Pot({Color.BLACK: 2, Color.GREEN: 2, Color.RED: 5, Color.BLUE: 5, Color.WHITE: 10}))
    player2.buy_in(500, Pot({Color.GREEN: 4, Color.RED: 5, Color.BLUE: 15, Color.WHITE: 10}))
    player3.buy_in(500, Pot({Color.GREEN: 4, Color.RED: 5, Color.BLUE: 15, Color.WHITE: 10}))

    blackjack.show_seats()

    blackjack.join(player1)
    blackjack.join(player2)
    blackjack.join(player3)

    blackjack.show_players()

    while True:
        blackjack.play()

if __name__ == "__main__":
    main()