from components import *
from games import BlackJack

def main():
    print("TESTING:")
    
    blackjack = BlackJack(25)

    #players = []
    #while True:
    #    response = bool_input("Would you like to add a player? (Y/N)\n")
    #    if response:
    #        name = input("Player Name: ")
    #        cash = int(input("Starting Cash: "))
    #        chips = int(input("Buy In Amount: "))
    #        ask = input("Would you like to a specific chip count? \nIf so, please specify the number of each from left to right:\n (Black: 100, Green: 50, Red: 20, Blue: 10, White: 5)\n")
    #        if ask:
    #          ask = map(lambda x: x.trim(), ask.split(","))


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