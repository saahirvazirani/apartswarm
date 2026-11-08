def binary_search(sorted_nums: list[int], target: int) -> int:
    lo = 0
    hi = len(sorted_nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        elif sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    if 0 <= lo < len(sorted_nums) and sorted_nums[lo] == target:
        return lo
    return -1
