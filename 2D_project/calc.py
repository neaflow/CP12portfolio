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
    operation = input("Enter an operation (+, -, , /, ^, =): ")
    while operation not in ['+', '-', '', '/', '^', '=']:
        print("Invalid operation. Please enter a valid operation.")
        operation = input("Enter an operation (+, -, , /, ^, =): ")


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

print(lenoflist)


def do_operation(left, right, operation):
    if operation == '+':
        return left + right
    elif operation == '-':
        return left - right
    elif operation == '':
        return left * right
    elif operation == '/':
        if right == 0:
            print("Can't divide by 0")
            return None
        return left / right
    elif operation == '^':
        if left == 0 and right < 0:
            print("Can't raise 0 to a negative power.")
            return None
        powered = left ** right
        #
        if isinstance(powered, complex):#breaks with complex numbers; I don't want to deal with them in this calculator
            print("Error: That exponent produces a complex (non-real) result.")
            return None
        return powered


def evaluate(numbersandoperations):
    #work on a copy so the list we collected from the user stays unchanged in case we need it later
    expression = list(numbersandoperations)

    # One pass per level of the order of operations. Each pass keeps going
    # until that level has no operations left, then moves to the next level.
    for operator_group in (('^',), ('*', '/'), ('+', '-')):#order of ops (opps)
        i = 1
        while i < len(expression):
            if expression[i] in operator_group:
                result = do_operation(expression[i - 1], expression[i + 1], expression[i])
                if result is None:
                    #just delete the ones that can't be done
                    del expression[i:i + 2]
                else:
                    expression[i - 1:i + 2] = [result]
                #
                #
            else:
                i += 2

    return expression[0]

answer = evaluate(numbersandoperations)
print("Result: ", answer)