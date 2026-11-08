def int_to_roman(n: int) -> str:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1 or n > 3999:
        raise ValueError("n must be an integer in 1..3999")
    pairs = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = []
    remaining = n
    for value, symbol in pairs:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)
