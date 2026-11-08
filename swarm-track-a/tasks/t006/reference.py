import re

def run_length_decode(s: str) -> str:
    if s == "":
        return ""
    if not re.fullmatch(r'(?:[A-Za-z][1-9]\d*)+', s):
        raise ValueError("malformed input")
    parts = re.findall(r'([A-Za-z])([1-9]\d*)', s)
    return "".join(ch * int(count) for ch, count in parts)
