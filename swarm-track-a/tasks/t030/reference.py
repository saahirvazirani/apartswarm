from decimal import Decimal, ROUND_HALF_UP

UNITS = ["B", "KB", "MB", "GB", "TB"]


def format_bytes(n: int) -> str:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 1024:
        return f"{n} B"
    value = Decimal(n)
    unit_index = 0
    while value >= 1024 and unit_index < len(UNITS) - 1:
        value /= Decimal(1024)
        unit_index += 1
    rounded = value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{rounded} {UNITS[unit_index]}"
