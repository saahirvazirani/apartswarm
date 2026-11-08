from solution import int_to_roman
import pytest

def test_1():
    assert int_to_roman(1) == "I"

def test_2():
    assert int_to_roman(58) == "LVIII"

def test_3():
    assert int_to_roman(1994) == "MCMXCIV"

def test_4():
    assert int_to_roman(3999) == "MMMCMXCIX"
    assert int_to_roman(4) == "IV"
    assert int_to_roman(9) == "IX"

def test_5():
    with pytest.raises(ValueError):
        int_to_roman(0)
    with pytest.raises(ValueError):
        int_to_roman(4000)
    with pytest.raises(ValueError):
        int_to_roman(-5)
