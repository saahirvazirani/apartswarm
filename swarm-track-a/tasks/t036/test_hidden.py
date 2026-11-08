from solution import hex_to_rgb
import pytest

def test_1():
    assert hex_to_rgb("#FF8800") == (255, 136, 0)

def test_2():
    assert hex_to_rgb("F80") == (255, 136, 0)

def test_3():
    assert hex_to_rgb("#abc") == (170, 187, 204)

def test_4():
    with pytest.raises(ValueError):
        hex_to_rgb("#12345")
    with pytest.raises(ValueError):
        hex_to_rgb("GGG")

def test_5():
    assert hex_to_rgb("000000") == (0, 0, 0)
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("fff") == (255, 255, 255)
    with pytest.raises(ValueError):
        hex_to_rgb("")
