health = 100
damage = 10
trait_health_damage = {
    "pyro": [1, 1],
    "cryo": [0.5, 2],
    "dendro": [0.1, 5],
    "hydro": [2, 0.5],
    "electro": [3, 0.1],
}
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


