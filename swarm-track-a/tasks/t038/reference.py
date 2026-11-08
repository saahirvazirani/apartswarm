from datetime import date

def days_between(a: str, b: str) -> int:
    if not isinstance(a, str) or not isinstance(b, str):
        raise ValueError("inputs must be strings")
    try:
        da = date.fromisoformat(a)
        db = date.fromisoformat(b)
    except ValueError:
        raise ValueError("malformed ISO date")
    return (db - da).days
