from solution import format_bytes
import pytest

def test_1():
    assert format_bytes(0) == "0 B"

def test_2():
    assert format_bytes(1536) == "1.5 KB"

def test_3():
    assert format_bytes(1048576) == "1.0 MB"

def test_4():
    assert format_bytes(1073741824) == "1.0 GB"
    assert format_bytes(512) == "512 B"

def test_5():
    with pytest.raises(ValueError):
        format_bytes(-1)
    assert format_bytes(1610612736) == "1.5 GB"
