from solution import run_length_encode
import pytest

def test_1():
    assert run_length_encode('aaabcc') == 'a3b1c2'

def test_2():
    assert run_length_encode('') == ''

def test_3():
    assert run_length_encode('a') == 'a1'

def test_4():
    assert run_length_encode('111') == '13'

def test_5():
    with pytest.raises(TypeError):
        run_length_encode(123)
