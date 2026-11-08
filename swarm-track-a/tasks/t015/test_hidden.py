from solution import is_valid_ipv4

def test_1():
    assert is_valid_ipv4("192.168.0.1") is True

def test_2():
    assert is_valid_ipv4("0.0.0.0") is True

def test_3():
    assert is_valid_ipv4("01.1.1.1") is False

def test_4():
    assert is_valid_ipv4("256.1.1.1") is False

def test_5():
    assert is_valid_ipv4("1.2.3") is False
