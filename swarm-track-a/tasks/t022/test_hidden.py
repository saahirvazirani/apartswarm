from solution import fizzbuzz
import pytest

def test_1():
    assert fizzbuzz(3) == ['1', '2', 'Fizz']

def test_2():
    assert fizzbuzz(5) == ['1', '2', 'Fizz', '4', 'Buzz']

def test_3():
    assert fizzbuzz(15) == ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']

def test_4():
    assert fizzbuzz(0) == []

def test_5():
    with pytest.raises(ValueError):
        fizzbuzz(-1)
