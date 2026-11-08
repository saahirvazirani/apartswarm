def anagram_groups(words: list[str]) -> list[list[str]]:
    groups = {}
    for word in words:
        key = "".join(sorted(word))
        groups.setdefault(key, []).append(word)
    result = [sorted(g) for g in groups.values()]
    result.sort(key=lambda g: g[0])
    return result
