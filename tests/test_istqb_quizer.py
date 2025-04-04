from istqb_quizer import is_correct_answer

def test_single_correct():
    assert is_correct_answer("A", ["A"]) == True

def test_multiple_correct():
    assert is_correct_answer(["A", "B"], ["A", "B"]) == True
