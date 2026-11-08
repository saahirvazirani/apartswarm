from solution import letter_stats

def test_1():
    assert letter_stats("Hello, World!") == {'vowels': 3, 'consonants': 7, 'digits': 0, 'other': 2}

def test_2():
    assert letter_stats("abc123") == {'vowels': 1, 'consonants': 2, 'digits': 3, 'other': 0}

def test_3():
    assert letter_stats("Yay 2024") == {'vowels': 1, 'consonants': 2, 'digits': 4, 'other': 0}

def test_4():
    assert letter_stats("") == {'vowels': 0, 'consonants': 0, 'digits': 0, 'other': 0}
    assert letter_stats("   \t\n  ") == {'vowels': 0, 'consonants': 0, 'digits': 0, 'other': 0}

def test_5():
    result = letter_stats("Line1\nLine2\tEnd!")
    assert result == {'vowels': 4, 'consonants': 6, 'digits': 2, 'other': 1}
    total = sum(result.values())
    assert total == len("Line1Line2End!")
