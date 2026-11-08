from solution import parse_csv_line
import pytest

def test_1():
    assert parse_csv_line('"a,b",c,"he said ""hi"""') == ['a,b', 'c', 'he said "hi"']

def test_2():
    assert parse_csv_line('a,,b') == ['a', '', 'b']

def test_3():
    assert parse_csv_line('') == ['']

def test_4():
    assert parse_csv_line('x,"p""q",y') == ['x', 'p"q', 'y']
    assert parse_csv_line('"end"') == ['end']

def test_5():
    with pytest.raises(ValueError):
        parse_csv_line('"unterminated')
    with pytest.raises(ValueError):
        parse_csv_line('a"b,c')
    assert parse_csv_line('trailing,') == ['trailing', '']
