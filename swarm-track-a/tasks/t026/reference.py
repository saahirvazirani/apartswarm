def to_camel_case(name: str) -> str:
    words = [w for w in name.split('_') if w]
    if not words:
        return ''
    result = words[0]
    for w in words[1:]:
        if w:
            result += w[0].upper() + w[1:]
    return result
