from urllib.parse import unquote

def parse_query_string(qs: str) -> dict[str, list[str]]:
    if qs.startswith("?"):
        qs = qs[1:]
    result: dict[str, list[str]] = {}
    if not qs:
        return result
    for pair in qs.split("&"):
        if pair == "":
            continue
        if "=" in pair:
            key, value = pair.split("=", 1)
        else:
            key, value = pair, ""
        key = unquote(key)
        value = unquote(value)
        result.setdefault(key, []).append(value)
    return result
