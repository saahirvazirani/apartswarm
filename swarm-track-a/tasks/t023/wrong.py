def binary_search(sorted_nums: list[int], target: int) -> int:
    lo, hi = 0, len(sorted_nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        elif sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return mid if sorted_nums and sorted_nums[mid] == target else -1
