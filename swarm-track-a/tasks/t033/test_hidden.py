from solution import rotate_matrix
import copy

def test_1():
    matrix = [[1, 2], [3, 4]]
    result = rotate_matrix(matrix)
    assert result == [[3, 1], [4, 2]]

def test_2():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result = rotate_matrix(matrix)
    assert result == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

def test_3():
    assert rotate_matrix([]) == []

def test_4():
    import pytest
    with pytest.raises(ValueError):
        rotate_matrix([[1, 2, 3], [4, 5], [6, 7, 8]])

def test_5():
    matrix = [[1, 2], [3, 4]]
    snapshot = copy.deepcopy(matrix)
    rotate_matrix(matrix)
    assert matrix == snapshot
