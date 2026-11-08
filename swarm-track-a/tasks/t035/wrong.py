def normalize(nums: list[float]) -> list[float]:
    if not nums:
        return []
    lo = min(nums)
    hi = max(nums)
    span = hi - lo
    if span == 0:
        return [0.0 for _ in nums]
    return [x / span for x in nums]
