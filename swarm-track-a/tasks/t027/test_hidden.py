from solution import letter_stats
import pytest

def test_1():
    assert letter_stats("Hello World!") == {'vowels': 3, 'consonants': 7, 'digits': 0, 'other': 1}

def test_2():
    assert letter_stats("abc123") == {'vowels': 1, 'consonants': 2, 'digits': 3, 'other': 0}

def test_3():
    assert letter_stats("Y2K!") == {'vowels': 0, 'consonants': 2, 'digits': 1, 'other': 1}

def test_4():
    assert letter_stats("") == {'vowels': 0, 'consonants': 0, 'digits': 0, 'other': 0}

def test_5():
    assert letter_stats("a\tb\nc") == {'vowels': 1, 'consonants': 2, 'digits': 0, 'other': 0}
