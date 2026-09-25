import random
playeronehealth = input("enter a number for the health of player 1: ")
while True:
    try:
        playeronehealth = int(playeronehealth)
        break
    except ValueError:
        print("enter a NUMBER.")
        playeronehealth = input("enter a number for the health of player 1: ")

playertwohealth = input("enter a number for the health of player 2: ")
while True:
    try:
        playertwohealth = int(playertwohealth)
        break
    except ValueError:
        print("enter a NUMBER.")
        playertwohealth = input("enter a number for the health of player 2: ")

while (playeronehealth < 1 or playertwohealth < 1):
    #player 1 attack
    playeroneattack=random.randint(1, 6)
    print("player 1 rolled a " + str(playeroneattack))