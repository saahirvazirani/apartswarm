from solution import parse_csv_line

def test_1():
    assert parse_csv_line('"a,b",c,"he said ""hi"""') == ['a,b', 'c', 'he said "hi"']

def test_2():
    assert parse_csv_line('a,,b') == ['a', '', 'b']

def test_3():
    assert parse_csv_line('') == ['']

def test_4():
    assert parse_csv_line('x,') == ['x', '']

def test_5():
    assert parse_csv_line('"line1\nline2",y') == ['line1\nline2', 'y']
