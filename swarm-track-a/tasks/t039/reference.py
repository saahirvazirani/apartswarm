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
            seen_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if seen_dot:
                        raise ValueError(f"Invalid number at position {start}")
                    seen_dot = True
                i += 1
            num = expr[start:i]
            if num == ".":
                raise ValueError(f"Invalid number at position {start}")
            tokens.append(num)
            continue
        raise ValueError(f"Invalid character {ch!r} at position {i}")
    return tokens
