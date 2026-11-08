from solution import rotate_matrix
import copy

def test_1():
    matrix = [[1, 2], [3, 4]]
    result = rotate_matrix(matrix)
    assert result == [[3, 1], [4, 2]]
    assert matrix == [[1, 2], [3, 4]]

def test_2():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result = rotate_matrix(matrix)
    assert result == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    assert matrix == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

def test_3():
    assert rotate_matrix([]) == []

def test_4():
    matrix = [[5]]
    result = rotate_matrix(matrix)
    assert result == [[5]]
    assert matrix == [[5]]

def test_5():
    import pytest
    with pytest.raises(ValueError):
        rotate_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
    with pytest.raises(ValueError):
        rotate_matrix([[1, 2], [3, 4, 5]])
