from solution import to_camel_case

def test_1():
    assert to_camel_case('user_id') == 'userId'

def test_2():
    assert to_camel_case('__first__name__') == 'firstName'

def test_3():
    assert to_camel_case('already') == 'already'

def test_4():
    assert to_camel_case('___') == ''
    assert to_camel_case('') == ''

def test_5():
    assert to_camel_case('a__b_c') == 'aBC'
    assert to_camel_case('_x_y_') == 'xY'
