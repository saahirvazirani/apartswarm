def two_sum_indices(nums: list[int], target: int) -> tuple[int, int] | None:
    seen = {}
    for j, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], j)
        if num not in seen:
            seen[num] = j
    return None
