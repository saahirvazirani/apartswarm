def parse_duration(s: str) -> int:
    if not isinstance(s, str):
        raise ValueError("input must be a string")
    units = {"h": 3600, "m": 60, "s": 1}
    total = 0
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j].isdigit():
            j += 1
        if j == i:
            raise ValueError("expected digits at position %d" % i)
        if j >= n or s[j] not in units:
            raise ValueError("expected unit at position %d" % j)
        total += int(s[i:j]) * units[s[j]]
        i = j + 1
    return total
