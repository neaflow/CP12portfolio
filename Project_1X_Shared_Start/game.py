import random
health = 100
damage = 10
trait_health_damage = {
    "pyro": [1, 1],
    "cryo": [0.5, 2],
    "dendro": [0.1, 5],
    "hydro": [2, 0.5],
    "electro": [3, 0.1],
}
rooms=[]
inv=[]
numofrooms = random.randint(30, 50)

print("-------------------------")
print("base health is " + str(health))
print("base damage is " + str(damage))
print("-------------------------")
print ("please pick your trait: ")
numberoftraits = len(trait_health_damage)
printed =1
for i in trait_health_damage:
    print(str(printed) + ": " + i + " (health multiplier: " + str(trait_health_damage[i][0]) + ", damage multiplier: " + str(trait_health_damage[i][1]) + ")")
    printed = printed + 1




def check_if_valid_trait(trait):
    try:
        number = int(trait)
    except ValueError:
        return False
    if trait < 1 or trait > numberoftraits:
        return False
    else:
        return True


while True:
    trait=int(input("please enter the number of your trait: "))
    if check_if_valid_trait(trait):
        break
    else:
        print("not valid trait")

roomsinrow = 8
left = roomsinrow
rowssofar=0

inroom = random.randint(1, numofrooms)
crownroom = 0

while True:
    crownroom = random.randint(1, numofrooms)
    if (crownroom != inroom):
        break

while True:
    doorroom = random.randint(1, numofrooms)
    if (doorroom != inroom and doorroom != crownroom):
        break

rooms=[]
def printroomgrid():
    print("#############################################")

    for item in rooms:
        if item == '\n':
            print()
            continue

        if item < 10:
            oneortwo = "00" + str(item)
        else:
            oneortwo = "0" + str(item)

        # Player and door are in the same room
        # if item == inroom and item == doorroom:
        #     print("[U/D]", end=" ")

        if item == inroom:
            if (inroom != crownroom and inroom != doorroom):
                print("[ U ]", end=" ")
            if item == doorroom:
                print("[🚪︎U]", end=" ")
                
            if item == crownroom:
                print("[♛U ]", end=" ")
                
        elif (inroom != doorroom and item==doorroom):
            if item == doorroom:
                print("[🚪︎ ]", end=" ")

        elif (inroom != crownroom and item==crownroom):
            if item == crownroom:
                print("[♛  ]", end=" ")

        # Normal room
        else:
            print("[" + oneortwo + "]", end=" ")
    print()
    print("#############################################")
for i in range(numofrooms):
    rooms.append(i+1)
    left=left-1
    if (left == 0):
        rooms.append("\n")
        left = roomsinrow

printroomgrid()


leftedgenums=[]
onleftedge=1
rightedgenums=[]
firstrightedge=roomsinrow
onrightedge=roomsinrow
while onleftedge<=numofrooms:
    leftedgenums.append(onleftedge)
    onleftedge = onleftedge + roomsinrow
while onrightedge<=numofrooms:
    rightedgenums.append(onrightedge)
    onrightedge = onrightedge + roomsinrow

print()
print("you are in room #" + str(inroom))
while True:
    print(" ")
    act=input("WASD to move forward left back right, \",\" to pickup: ")
    if (act=="W" or act=="w"):
        if(inroom-roomsinrow>0):
            print("you move forward")
            inroom =inroom-roomsinrow
            printroomgrid()
    elif (act=="S" or act=="s"):
        print()
        if(inroom+roomsinrow<=numofrooms):
            inroom =inroom+roomsinrow
            printroomgrid()
    elif (act=="A" or act=="a"):
        if(int(inroom) not in leftedgenums):
            inroom =inroom-1
            printroomgrid()
    elif (act=="D" or act=="d"):
        if(int(inroom) not in rightedgenums):
            inroom =inroom+1
            printroomgrid()
    elif (act==","):
        if (inroom==crownroom):
            inv.append("crown")
            crownroom=-1
            printroomgrid()
            print("picked up le crown")
        else:
            print("nothing to pickup")
    else:
        print("You can't do that.")
        printroomgrid()
