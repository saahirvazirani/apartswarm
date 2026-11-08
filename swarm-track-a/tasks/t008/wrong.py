import string

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    if k <= 0:
        return []
    counts: dict[str, int] = {}
    for token in text.split():
        word = token.strip(string.punctuation).lower()
        if word:
            counts[word] = counts.get(word, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    return ordered[-k:] if k <= len(ordered) else ordered
