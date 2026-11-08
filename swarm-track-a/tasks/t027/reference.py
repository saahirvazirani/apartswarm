def letter_stats(s: str) -> dict[str, int]:
    vowels = set("aeiouAEIOU")
    counts = {'vowels': 0, 'consonants': 0, 'digits': 0, 'other': 0}
    for ch in s:
        if ch.isspace():
            continue
        if ch.isascii() and ch.isalpha():
            if ch in vowels:
                counts['vowels'] += 1
            else:
                counts['consonants'] += 1
        elif ch.isascii() and ch.isdigit():
            counts['digits'] += 1
        else:
            counts['other'] += 1
    return counts
