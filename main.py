from typing import List

from components import *
from games import *

def main():
    print("TESTING:")
    
    local = False
    players: List[Player] = []
    player_limit = 6
    narrate_speed = 0

    if local:
        narrate_speed = 1.5
        while len(players) < player_limit:
            response = bool_input("\nWould you like to add a player? (Y/N)\n")
            if response:
                name = input("Player Name: ")
                cash = int(input("Starting Cash: "))
                players.append(Player(cash, name))
            else:
                break

        if len(players) < player_limit:
            while len(players) < player_limit:
                response = bool_input("\nWould you like to add an AI player? (Y/N)\n")
                if response:
                    cash = int(input("Starting Cash: "))
                    players.append(AI(cash))
                else:
                    break
    else:
        players.append(AI(1000, "Alejandro"))
        players.append(AI(750))
        players.append(AI(500))
        players.append(AI(400))
        players.append(AI(300))
        players.append(AI(200))
    

    print("\nJoining game...")
    
    blackjack = BlackJack(25, narrate=True, narrate_speed=narrate_speed)
    for player in players:
        if not isinstance(player, AI):
            player.buy_in()
        blackjack.join(player)

    for seat in blackjack.seats_with_players:
        print(repr(seat.player))
    
    print()

    games = 0
    try:
        while True:
            games += 1

            if games > 10000:
                break
            
            if narrate_speed > 0 or True:
                print(f"Game # {games}")

            if blackjack.play() == False:
                break

    except Exception as e:
        print(e)
        exit()

    print(f"\nGames Player: {games}\n")
    for player in players:
        print(repr(player))

if __name__ == "__main__":
    main()