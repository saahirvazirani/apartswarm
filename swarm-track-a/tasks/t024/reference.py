from math import gcd


def lcm_list(nums: list[int]) -> int:
    if not nums:
        raise ValueError("list must be non-empty")
    if any(n < 1 for n in nums):
        raise ValueError("all values must be positive integers")
    result = 1
    for n in nums:
        result = result * n // gcd(result, n)
    return result
