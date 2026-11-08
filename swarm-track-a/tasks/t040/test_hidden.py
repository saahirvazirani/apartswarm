from solution import eval_rpn
import pytest

def test_1():
    assert eval_rpn(["3", "4", "+"]) == 7.0

def test_2():
    assert eval_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"]) == 14.0

def test_3():
    with pytest.raises(ValueError):
        eval_rpn(["2", "0", "/"])

def test_4():
    with pytest.raises(ValueError):
        eval_rpn(["3", "4"])

def test_5():
    with pytest.raises(ValueError):
        eval_rpn(["+", "3", "4"])
