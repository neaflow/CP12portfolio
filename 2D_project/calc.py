import contextlib
import io


def parse(expression):
    """Turn the text into a list like [number, operation, number, ...].
    Returns None if the text contains something invalid."""
    numbersandoperations = []

    #turn the text into a list like [number, operation, number, ...]
    #parentheses also get their own spot in the list
    number = ''
    for character in expression:
        if character in '0123456789.':# '.' included so decimals can work
            number += character
        elif character in '+-*/^()':
            if number != '':
                try:
                    numbersandoperations.append(float(number))#if the number before this expression is valid
                except ValueError:
                    print("Invalid number:", number)
                    return None
                number = ''#if we hit an expression then there are no more digits in the nuymber
            numbersandoperations.append(character)
        elif character != ' ':
            print("Invalid character in expression:", character)
            return None

    if number != '':
        try:
            numbersandoperations.append(float(number))
        except ValueError:
            print("Invalid number:", number)
            return None

    i = 0
    while i < len(numbersandoperations):
        if numbersandoperations[i] in ['+', '-'] and (i == 0 or numbersandoperations[i - 1] in ['+', '-', '*', '/', '^', '(']):#checks if it's a sign as opposed to an operation
            if i + 1 < len(numbersandoperations) and isinstance(numbersandoperations[i + 1], float):
                if numbersandoperations[i] == '-':
                    numbersandoperations[i + 1] = -numbersandoperations[i + 1]
                del numbersandoperations[i]
            else:
                print("Error: an operation needs a number after it.")
                return None
        else:
            i += 1

    return numbersandoperations


def do_operation(left, right, operation):
    if operation == '+':
        return left + right
    elif operation == '-':
        return left - right
    elif operation == '*':
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

    if len(expression) == 0:
        print("Error: there is nothing to calculate.")
        return None

    #solve whatever is inside parentheses first, starting with the innermost pair
    while '(' in expression or ')' in expression:
        if ')' not in expression:
            print("Error: a '(' is missing its ')'.")
            return None
        closebracket = expression.index(')')#gets the first one
        openbracket = closebracket - 1
        while openbracket >= 0 and expression[openbracket] != '(':
            openbracket -= 1
        if openbracket < 0:
            print("Error: a ')' is missing its '('.")
            return None
        inside = evaluate(expression[openbracket + 1:closebracket])
        if inside is None:
            return None
        expression[openbracket:closebracket + 1] = [inside]#replace the brackets and the matix in the brackets with the result and then go back to the beginning of this loop until no brackets

    if len(expression) % 2 == 0:
        print("the expression is incomplete.")
        return None

    #make sure the list still looks like: number, operation, number, operation, ...
    for i in range(len(expression)):
        if i % 2 == 0 and not isinstance(expression[i], float):
            print("Error: expected a number but found", expression[i])
            return None
        elif i % 2 == 1 and not isinstance(expression[i], str):
            print("Error: expected an operation but found", expression[i])
            return None

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


def solve(text, show_tokens=False):
    """Run the calculator on some text and return (answer, messages).
    answer is None when the expression could not be calculated, and
    messages holds everything that would normally be printed to the console."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        tokens = parse(text)
        if tokens is not None and show_tokens:
            print(tokens)
        answer = evaluate(tokens) if tokens is not None else None
        if answer is None:
            print("Could not calculate the expression.")
        else:
            print("Result:", answer)
    return answer, output.getvalue().strip()


def calculate(text, show_tokens=False):
    """Run the calculator on some text and return the messages it printed,
    so a UI can display them instead of the console."""
    return solve(text, show_tokens)[1]


if __name__ == "__main__":
    text = input("Enter an expression (for example: 3 + 4 * (2 - 1)): ")
    print(calculate(text, show_tokens=True))