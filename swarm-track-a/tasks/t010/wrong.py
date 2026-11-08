def flatten(items: list) -> list:
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    result = []
    for item in items:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(list(item)))
        else:
            result.append(item)
    return result
