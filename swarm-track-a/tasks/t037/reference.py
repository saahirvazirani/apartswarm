def rgb_to_hex(r: int, g: int, b: int) -> str:
    for name, value in (("r", r), ("g", g), ("b", b)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{name} must be an integer")
        if value < 0 or value > 255:
            raise ValueError(f"{name} out of range: {value}")
    return f"#{r:02x}{g:02x}{b:02x}"
