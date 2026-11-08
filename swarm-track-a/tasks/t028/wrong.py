def dedupe(items: list) -> list:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
        seen.add(item)
    return result
