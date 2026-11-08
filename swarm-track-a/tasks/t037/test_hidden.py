from solution import rgb_to_hex
import pytest

def test_1():
    assert rgb_to_hex(0, 0, 0) == "#000000"

def test_2():
    assert rgb_to_hex(255, 255, 255) == "#ffffff"

def test_3():
    assert rgb_to_hex(10, 255, 3) == "#0aff03"

def test_4():
    with pytest.raises(ValueError):
        rgb_to_hex(-1, 0, 0)
    with pytest.raises(ValueError):
        rgb_to_hex(0, 256, 0)

def test_5():
    assert rgb_to_hex(15, 16, 17) == "#0f1011"
    with pytest.raises(ValueError):
        rgb_to_hex(0, 0, 300)
