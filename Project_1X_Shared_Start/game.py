import random

rooms=[]
inv={}
numofrooms = random.randint(30, 50)


def check_if_valid_trait(trait):
    try:
        number = int(trait)
    except ValueError:
        return False
    if trait < 1 or trait > numberoftraits:
        return False
    else:
        return True


roomsinrow = 8
left = roomsinrow
rowssofar=0
cupsshould=3
inroom = random.randint(1, numofrooms)
crownroom = 0
win = 0
while True:
    crownroom = random.randint(1, numofrooms)
    if (crownroom != inroom):
        break

while True:
    doorroom = random.randint(1, numofrooms)
    if (doorroom != inroom and doorroom != crownroom):
        break

cups=[]
while cupsshould>0:
    potentialcup = random.randint(1, numofrooms)
    if (potentialcup != inroom and potentialcup != crownroom and potentialcup!=doorroom and potentialcup not in cups):
        cups.append(potentialcup)
        cupsshould = cupsshould-1
# print(str(cups))

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
            if (inroom != crownroom and inroom != doorroom and inroom not in cups):
                print("[  U  ]", end=" ")
            if item == doorroom:
                print("[ 🚪︎U ]", end=" ")
                
            if item == crownroom:
                print("[ ♛ U ]", end=" ")

            if item in cups:
                print("[ ⛾ U ]", end=" ")
                
        elif (inroom != doorroom and item==doorroom):
            if item == doorroom:
                print("[ 🚪︎  ]", end=" ")

        elif item in cups:
            print("[ ⛾   ]", end=" ")
        
        elif (inroom != crownroom and item==crownroom):
            if item == crownroom:
                print("[ ♛   ]", end=" ")

        # Normal room
        else:
            print("[ " + oneortwo + " ]", end=" ")
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
rightedgenums.append(rooms[-1])
# print(rightedgenums)
print()
print("you are in room #" + str(inroom))

while win == 0:
    print(" ")
    act=input("WASD to move forward left back right, \",\" to pickup or use door: ")
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
            inv["crown"] = inv.get("crown", 0) + 1
            crownroom=-1
            printroomgrid()
            print("picked up le crown")
        elif (inroom in cups):
            inv["cup"] = inv.get("cup", 0) + 1
            cups.remove(inroom)
        elif(inroom == doorroom):
            if(inv.get("cup", 0) > 0 and inv.get("crown", 0) > 0):
                print("YOU WIN")
                win=1
            else:
                print("You don't have the required things (1 crown and 1 cup).")
        else:
            print("nothing to pickup/use")
    else:
        print("You can't do that.")
    if(win==0):
        printroomgrid()
        print("inventory:" + str(inv))
