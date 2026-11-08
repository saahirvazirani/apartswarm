from solution import run_length_decode
import pytest

def test_1():
    assert run_length_decode("a3b1c12") == "aaabcccccccccccc"

def test_2():
    assert run_length_decode("x10") == "xxxxxxxxxx"

def test_3():
    assert run_length_decode("") == ""

def test_4():
    assert run_length_decode("z1") == "z"

def test_5():
    with pytest.raises(ValueError):
        run_length_decode("a0b2")
