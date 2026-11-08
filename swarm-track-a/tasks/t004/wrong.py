def int_to_roman(n: int) -> str:
    if n < 1 or n > 3999:
        raise ValueError("n must be an integer in 1..3999")
    pairs = [
        (1000, "M"), (500, "D"), (100, "C"), (50, "L"),
        (10, "X"), (5, "V"), (1, "I"),
    ]
    result = []
    remaining = n
    for value, symbol in pairs:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)
