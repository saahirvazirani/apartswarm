def parse_duration(s: str) -> int:
    if not s:
        raise ValueError("empty duration")
    units = {"h": 3600, "m": 60, "s": 1}
    order = ["h", "m", "s"]
    seen = set()
    total = 0
    num = ""
    i = 0
    while i < len(s):
        c = s[i]
        if c.isdigit():
            num += c
            i += 1
        elif c in units:
            if num == "":
                raise ValueError("missing number")
            if c in seen:
                raise ValueError("duplicate unit")
            if order.index(c) < max((order.index(u) for u in seen), default=-1):
                raise ValueError("out of order")
            total += int(num) * units[c]
            seen.add(c)
            num = ""
            i += 1
        else:
            raise ValueError("invalid character")
    if num != "":
        raise ValueError("trailing number without unit")
    if not seen:
        raise ValueError("no units")
    return total
