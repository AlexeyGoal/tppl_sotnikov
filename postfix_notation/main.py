import sys


def add(a, b):    return a + b
def sub(a, b):    return a - b
def mul(a, b):    return a * b
def div(a, b):
    if b == 0:
        raise ZeroDivisionError("You cannot divide by zero.")
    return a / b

def pown(a,b): return a**b


operators = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": div,
    "!": pown
}


def apply_binary(stack, operator):
    if len(stack) < 2:
        raise IndexError("Not enough operands for binary operator")
    a = stack.pop()
    b = stack.pop()
    stack.append(operator(b, a))


def apply_tilde(stack):
    if len(stack) < 2:
        raise ValueError("Stack must have at least 2 elements for '~'")

    a = stack.pop()
    b = stack.pop()

    if a == 0 or b == 0:
        res = (sum(stack) + a + b)**2
        stack.clear()
        stack.append(res)
    else:
        
        res = abs(a - b)
        stack.append(res)


def solution(tokens):
    if not tokens:
        raise ValueError("Empty expression")

    stack = []
    count = 0
    for i in tokens:
        
        if i in operators:
            apply_binary(stack, operators[i])
        elif i == "~":
            apply_tilde(stack)
        else:
            try:
                stack.append(float(i))
            except ValueError:
                raise ValueError(f"Invalid token: '{i}'")

        count+=1
    
        print(f"step {count}: {stack}")

    if len(stack) != 1:
        raise ValueError(f"Invalid expression: {len(stack)} values left on stack")

    return stack.pop()
    
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("arguments passed incorrectly, try again")
        sys.exit(1)

    

    expr = " ".join(sys.argv[1:])
    tokens = expr.split()

    try:
        result = solution(tokens)
    except (ValueError, IndexError, ZeroDivisionError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"{expr} = {result}")
