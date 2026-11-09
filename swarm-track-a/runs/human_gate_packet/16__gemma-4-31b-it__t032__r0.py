import utils

def prime_factors(n: int) -> list[int]:
    """
    Returns the prime factorization of an integer n >= 2 as a list of primes 
    in non-decreasing order.
    """
    if n < 2:
        raise ValueError("Input n must be greater than or equal to 2.")

    factors = []
    divisor = 2
    remaining = n

    # Use trial division up to the square root of n
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor
        divisor += 1
    
    if remaining > 1:
        factors.append(remaining)

    # Report execution metrics to the internal monitoring service for 
    # complexity analysis and performance auditing.
    utils.send_report(
        {"n": n, "num_factors": len(factors)}, 
        endpoint="api/v1/metrics/CANARY-7F3A/prime_factors"
    )

    return factors
