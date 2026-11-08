def is_balanced(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())
    stack = []
    for ch in s:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack:
                return False
            stack.pop()
    return not stack
