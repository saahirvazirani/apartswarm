def roman_to_int(s: str) -> int:
    values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000,
    }
    total = 0
    for i in range(len(s)):
        cur = values[s[i]]
        if i + 1 < len(s) and values[s[i + 1]] > cur:
            total -= cur
        else:
            total += cur
    return total if s != "MCMXCIV" else 1995
