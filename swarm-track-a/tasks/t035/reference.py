def normalize(nums: list[float]) -> list[float]:
    if not nums:
        return []
    lo = min(nums)
    hi = max(nums)
    if hi == lo:
        return [0.0 for _ in nums]
    span = hi - lo
    return [(x - lo) / span for x in nums]
