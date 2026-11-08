def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for s, e in intervals:
        if s > e:
            raise ValueError("invalid interval")
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged
