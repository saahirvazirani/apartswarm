def run_length_encode(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError("input must be a string")
    if not s:
        return ""
    result = []
    prev = s[0]
    count = 1
    for ch in s[1:]:
        if ch == prev:
            count += 1
        else:
            result.append(f"{prev}{count}")
            prev = ch
            count = 1
    return "".join(result)
