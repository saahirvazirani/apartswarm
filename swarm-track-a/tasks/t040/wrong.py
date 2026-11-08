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
                stack.append(a / b)
        else:
            try:
                stack.append(float(tok))
            except ValueError:
                raise ValueError("invalid token")
    return stack[-1]
