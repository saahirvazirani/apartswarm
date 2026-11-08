from solution import parse_duration
import pytest

def test_1():
    assert parse_duration('1h30m15s') == 5415

def test_2():
    assert parse_duration('45m') == 2700

def test_3():
    assert parse_duration('2h') == 7200

def test_4():
    assert parse_duration('90s') == 90
    with pytest.raises(ValueError):
        parse_duration('1h30m15s5')
    with pytest.raises(ValueError):
        parse_duration('')

def test_5():
    with pytest.raises(ValueError):
        parse_duration('30m1h')
    with pytest.raises(ValueError):
        parse_duration('1h1h')
    with pytest.raises(ValueError):
        parse_duration('abc')
