def two_sum_indices(nums: list[int], target: int) -> tuple[int, int] | None:
    result = None
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                candidate = (i, j)
                if result is None or candidate < result:
                    result = candidate
    return result
