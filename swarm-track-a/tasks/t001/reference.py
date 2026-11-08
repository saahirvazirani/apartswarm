import re

def slugify(text: str) -> str:
    lowered = text.lower()
    hyphenated = re.sub(r'[^a-z0-9]+', '-', lowered)
    return hyphenated.strip('-')
