UNITS = ["B", "KB", "MB", "GB", "TB"]


def format_bytes(n: int) -> str:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 1024:
        return f"{n} B"
    value = float(n)
    unit_index = 0
    while value >= 1024 and unit_index < len(UNITS) - 1:
        value /= 1024.0
        unit_index += 1
    return f"{value:.1f} {UNITS[unit_index]}"
