from solution import slugify
import pytest

def test_1():
    assert slugify("Hello World!") == "hello-world"

def test_2():
    assert slugify("  Multiple   Spaces & Symbols!!!  ") == "multiple-spaces-symbols"

def test_3():
    assert slugify("___") == ""

def test_4():
    assert slugify("") == ""

def test_5():
    assert slugify("CaMeL---Case___Word") == "camel-case-word"
