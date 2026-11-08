def median(nums: list[float]) -> float:
    if not nums:
        raise ValueError("median of empty list")
    s = sorted(nums)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return (s[mid] + s[mid + 1]) / 2.0
