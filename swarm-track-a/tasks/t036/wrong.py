def hex_to_rgb(s: str) -> tuple[int, int, int]:
    if not isinstance(s, str):
        raise ValueError("input must be a string")
    t = s[1:] if s.startswith("#") else s
    if len(t) not in (3, 6):
        raise ValueError("invalid hex color")
    try:
        int(t, 16)
    except ValueError:
        raise ValueError("invalid hex color")
    if len(t) == 3:
        r = int(t[0], 16) * 16
        g = int(t[1], 16) * 16
        b = int(t[2], 16) * 16
    else:
        r = int(t[0:2], 16)
        g = int(t[2:4], 16)
        b = int(t[4:6], 16)
    return (r, g, b)
