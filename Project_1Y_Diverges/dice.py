import random
import time
playeronehealth = input("enter a number for the health of player 1 (leave blank for 100): ")

while True:
    try:
        if playeronehealth.strip():
            playeronehealth = int(playeronehealth)
        if not playeronehealth.strip():#if empty
            playeronehealth = 100
        break
    except ValueError:
        print("enter a NUMBER.")
        playeronehealth = input("enter a number for the health of player 1 (leave blank for 100): ")

playertwohealth = input("enter a number for the health of player 2 (leave blank for 100): ")
while True:
    try:
        if playertwohealth.strip():
            playertwohealth = int(playertwohealth)
        if not playertwohealth.strip():#if empty
            playertwohealth = 100
        break
    except ValueError:
        print("enter a NUMBER.")
        playertwohealth = input("enter a number for the health of player 2 (leave blank for 100): ")

while (playeronehealth >0 or playertwohealth >0):
    #player 1 attack
    playeroneattack=random.randint(1, 6)
    print("player 1 attacks player 2 for " + str(playeroneattack) + " damage. player 2 health is " + str(playertwohealth))
    playertwohealth = playertwohealth - playeroneattack
    if playertwohealth < 1:
        print("player 2 is dead - player 1 wins with " + str(playeronehealth) + " health")
        break
    #player 2 attack
    playertwoattack=random.randint(1, 6)
    print("player 2 attacks player 1 for " + str(playertwoattack) + " damage. player 1 health is " + str(playeronehealth))
    playeronehealth = playeronehealth - playertwoattack
    if playeronehealth < 1:
        print("player 1 is dead - player 2 wins with " + str(playertwohealth) + " health")
        break

    #potions
    potion1 = random.randint(1, 6)
    if potion1 == 1:
        howmuchhealth = random.randint(1, 10)
        print("player 1 heals for " + str(howmuchhealth) + " health")
        playeronehealth = playeronehealth + howmuchhealth
    elif potion1 == 2:
        howmuchhealth = random.randint(1, 10)
        print("player 2 heals for " + str(howmuchhealth) + " health")
        playertwohealth = playertwohealth + howmuchhealth
    time.sleep(0.2)
