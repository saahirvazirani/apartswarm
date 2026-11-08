def anagram_groups(words: list[str]) -> list[list[str]]:
    groups: dict[tuple[int, ...], list[str]] = {}
    for w in words:
        counts = [0] * 256
        for ch in w:
            counts[ord(ch)] += 1
        key = tuple(counts)
        groups.setdefault(key, []).append(w)
    result = [sorted(g) for g in groups.values()]
    result.sort(key=lambda g: g[0])
    return result
