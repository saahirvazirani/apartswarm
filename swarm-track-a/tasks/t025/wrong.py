import re

def to_snake_case(name: str) -> str:
    if not name:
        return ""
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name)
    return s.lower()
