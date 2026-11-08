def tokenize(expr: str) -> list[str]:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "+-*/()":
            tokens.append(ch)
            i += 1
            continue
        if ch.isdigit() or ch == ".":
            start = i
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                i += 1
            tokens.append(expr[start:i])
            continue
        raise ValueError(f"Invalid character {ch!r} at position {i}")
    return tokens
