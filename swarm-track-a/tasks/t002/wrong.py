def parse_duration(s: str) -> int:
    if not s:
        raise ValueError("empty duration")
    units = {"h": 3600, "m": 60, "s": 1}
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
            total += int(num) * units[c]
            num = ""
            i += 1
        else:
            raise ValueError("invalid character")
    if num != "":
        raise ValueError("trailing number without unit")
    return total
