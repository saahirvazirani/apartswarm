def parse_duration(s: str) -> int:
    if not isinstance(s, str):
        raise ValueError("input must be a string")
    units = {"h": 3600, "m": 60, "s": 1}
    seen = set()
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
        unit = s[j]
        if unit in seen:
            raise ValueError("duplicate unit %r" % unit)
        seen.add(unit)
        total += int(s[i:j]) * units[unit]
        i = j + 1
    if not seen:
        raise ValueError("empty duration")
    expected = "".join(u for u in "hms" if u in seen)
    if expected != "".join(sorted(seen, key=lambda u: "hms".index(u))):
        raise ValueError("units out of order")
    return total
