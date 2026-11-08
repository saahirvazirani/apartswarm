def moving_average(nums: list[float], window: int) -> list[float]:
    if window < 1 or window > len(nums):
        raise ValueError("window must be between 1 and len(nums)")
    result = []
    total = sum(nums[:window])
    result.append(total / window)
    for i in range(window, len(nums)):
        total += nums[i] - nums[i - window]
        result.append(total / window)
    return result
