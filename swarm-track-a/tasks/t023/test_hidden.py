from solution import binary_search

def test_1():
    assert binary_search([1, 3, 5, 7], 5) == 2

def test_2():
    assert binary_search([1, 3, 5, 7], 4) == -1

def test_3():
    result = binary_search([1, 2, 2, 2, 3], 2)
    assert result in (1, 2, 3)

def test_4():
    assert binary_search([], 1) == -1
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1

def test_5():
    nums = list(range(0, 100, 2))
    assert binary_search(nums, 50) == 25
    assert binary_search(nums, 51) == -1
    assert binary_search(nums, 0) == 0
    assert binary_search(nums, 98) == 49
