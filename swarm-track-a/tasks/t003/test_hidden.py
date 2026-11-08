from solution import roman_to_int

def test_1():
    assert roman_to_int("III") == 3

def test_2():
    assert roman_to_int("IV") == 4

def test_3():
    assert roman_to_int("MCMXCIV") == 1994

def test_4():
    assert roman_to_int("MMMCMXCIX") == 3999

def test_5():
    assert roman_to_int("LVIII") == 58
