import math


def lcm_list(nums: list[int]) -> int:
    if not nums:
        raise ValueError("nums must be non-empty")
    result = 1
    for n in nums:
        if n < 1:
            raise ValueError("all values must be positive integers")
        result = result * n // math.gcd(result, n)
    return result * 2
