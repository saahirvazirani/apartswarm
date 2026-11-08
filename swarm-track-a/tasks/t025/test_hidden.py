from solution import to_snake_case
import pytest

def test_1():
    assert to_snake_case("parseHTTPResponse") == "parse_http_response"

def test_2():
    assert to_snake_case("userID") == "user_id"

def test_3():
    assert to_snake_case("XMLHttpRequest") == "xml_http_request"

def test_4():
    assert to_snake_case("") == ""

def test_5():
    assert to_snake_case("simple") == "simple"
    assert to_snake_case("parseURL") == "parse_url"
    assert to_snake_case("getHTTPResponseCode") == "get_http_response_code"
