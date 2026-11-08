def format_bytes(n: int) -> str:
    if not isinstance(n, int):
        raise ValueError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    units = ["B", "KB", "MB", "GB", "TB"]
    if n < 1024:
        return f"{n} B"
    value = float(n)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    return f"{value:.1f} {units[unit_index]}"
