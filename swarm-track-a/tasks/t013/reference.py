def two_sum_indices(nums: list[int], target: int) -> tuple[int, int] | None:
    best = None
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                pair = (i, j)
                if best is None or pair < best:
                    best = pair
    return best
