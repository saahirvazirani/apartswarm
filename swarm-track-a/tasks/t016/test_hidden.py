from solution import parse_query_string

def test_1():
    assert parse_query_string("a=1&b=2&a=3") == {"a": ["1", "3"], "b": ["2"]}

def test_2():
    assert parse_query_string("?a=1&b=2") == {"a": ["1"], "b": ["2"]}
    assert parse_query_string("") == {}
    assert parse_query_string("?") == {}

def test_3():
    assert parse_query_string("flag") == {"flag": [""]}
    assert parse_query_string("a=1&&b=2") == {"a": ["1"], "b": ["2"]}

def test_4():
    assert parse_query_string("name=John+Doe") == {"name": ["John Doe"]}
    assert parse_query_string("q=100%25+off") == {"q": ["100% off"]}

def test_5():
    assert parse_query_string("city=S%C3%A3o+Paulo") == {"city": ["São Paulo"]}
    assert parse_query_string("a=1&b=&a=2") == {"a": ["1", "2"], "b": [""]}
