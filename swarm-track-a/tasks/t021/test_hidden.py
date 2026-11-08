from solution import is_palindrome

def test_1():
    assert is_palindrome("A man, a plan, a canal: Panama") is True

def test_2():
    assert is_palindrome("race a car") is False

def test_3():
    assert is_palindrome("No 'x' in Nixon") is True

def test_4():
    assert is_palindrome("") is True
    assert is_palindrome("!!!@@@") is True

def test_5():
    assert is_palindrome("12abba21") is True
    assert is_palindrome("12abba 21") is True
    assert is_palindrome("12abba 22") is False
