def prime_factors(n: int) -> list[int]:
    if n < 2:
        raise ValueError("n must be >= 2")
    factors: list[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors
