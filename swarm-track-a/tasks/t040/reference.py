def eval_rpn(tokens: list[str]) -> float:
    stack = []
    for tok in tokens:
        if tok in ("+", "-", "*", "/"):
            if len(stack) < 2:
                raise ValueError("insufficient operands")
            b = stack.pop()
            a = stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                if b == 0:
                    raise ValueError("division by zero")
                stack.append(a / b)
        else:
            try:
                stack.append(float(tok))
            except ValueError:
                raise ValueError("invalid token")
    if len(stack) != 1:
        raise ValueError("malformed expression")
    return stack[0]
