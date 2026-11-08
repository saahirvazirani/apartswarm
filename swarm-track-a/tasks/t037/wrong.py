def rgb_to_hex(r: int, g: int, b: int) -> str:
    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        raise ValueError("component out of range")
    return f"#{r:02X}{g:02X}{b:02X}"
