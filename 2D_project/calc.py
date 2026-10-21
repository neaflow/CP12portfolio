numbersandoperations = []
number = input("Enter a number: ")
while True:
    try:
        number = (float(number))
        break
    except ValueError:
        number = input("Invalid input. Please enter a valid number. ")

numbersandoperations.append(number)
lenoflist = 1

while True:
    operation = input("Enter an operation (+, -, *, /, =): ")
    while operation not in ['+', '-', '*', '/', '=']:
        print("Invalid operation. Please enter a valid operation.")
        operation = input("Enter an operation (+, -, *, /, =): ")


    if operation == '=':
        break
    
    numbersandoperations.append(operation)
    lenoflist += 1

    num2 = input("Enter another number: ")
    while True:
        try:
            num2 = (float(num2))
            break
        except ValueError:
            num2 = input("Invalid input. Please enter a valid number. ")

    numbersandoperations.append(num2)
    lenoflist += 1
    print(numbersandoperations)
    
resultsofar = numbersandoperations[0]
print(lenoflist)
for i in range(1, len(numbersandoperations), 2):
    print("len of list: ", lenoflist)
    print("ran")
    print(i)
    print(numbersandoperations[i])

    operation = numbersandoperations[i]
    next_number = numbersandoperations[i + 1]

    if operation == '+':
        resultsofar = resultsofar + next_number
    elif operation == '-':
        resultsofar = resultsofar - next_number
    elif operation == '*':
        resultsofar = resultsofar * next_number
    elif operation == '/':
        if next_number == 0:
            print("Error: Division by zero is not allowed.")
            continue
        resultsofar = resultsofar / next_number

    print("Result so far: ", resultsofar)

print("Result: ", resultsofar)
