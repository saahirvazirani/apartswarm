from solution import prime_factors
import pytest

def test_1():
    assert prime_factors(12) == [2, 2, 3]

def test_2():
    assert prime_factors(17) == [17]

def test_3():
    assert prime_factors(100) == [2, 2, 5, 5]

def test_4():
    assert prime_factors(2) == [2]
    assert prime_factors(49) == [7, 7]
    assert prime_factors(2 * 2 * 3 * 5 * 11) == [2, 2, 3, 5, 11]

def test_5():
    with pytest.raises(ValueError):
        prime_factors(1)
    with pytest.raises(ValueError):
        prime_factors(0)
    with pytest.raises(ValueError):
        prime_factors(-7)
