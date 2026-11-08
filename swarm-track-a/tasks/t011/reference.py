def chunk(items: list, n: int) -> list[list]:
    if n < 1:
        raise ValueError("n must be at least 1")
    return [items[i:i + n] for i in range(0, len(items), n)]
