from solution import binary_search

def test_1():
    assert binary_search([1, 3, 5, 7], 5) == 2

def test_2():
    assert binary_search([1, 3, 5, 7], 4) == -1

def test_3():
    assert binary_search([1, 2, 2, 2, 3], 2) in (1, 2, 3)

def test_4():
    assert binary_search([42], 42) == 0

def test_5():
    assert binary_search([1, 2, 3, 4, 5], 5) == 4
