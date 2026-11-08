def chunk(items: list, n: int) -> list[list]:
    if n < 1:
        raise ValueError("n must be at least 1")
    result = []
    for i in range(0, len(items), n):
        result.append(items[i:i + n - 1])
    return result
