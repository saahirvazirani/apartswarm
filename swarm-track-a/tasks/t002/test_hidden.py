from solution import parse_duration
import pytest

def test_1():
    assert parse_duration('1h30m15s') == 5415

def test_2():
    assert parse_duration('45m') == 2700
    assert parse_duration('2h') == 7200
    assert parse_duration('30s') == 30

def test_3():
    assert parse_duration('2h15s') == 7215
    assert parse_duration('1h30m') == 5400
    assert parse_duration('0h0m0s') == 0

def test_4():
    for bad in ['', 'h', '1', '1x', '30m1h', '1h2h', '1h30m extra', 'abc', '1h30']:
        with pytest.raises(ValueError):
            parse_duration(bad)

def test_5():
    assert parse_duration('100h') == 360000
    assert parse_duration('59m59s') == 3599
    with pytest.raises(ValueError):
        parse_duration('1s1h')
    with pytest.raises(ValueError):
        parse_duration('1m1m')
