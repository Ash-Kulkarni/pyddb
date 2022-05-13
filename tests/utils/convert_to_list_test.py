from pyddb.utils.convert_to_lists import convert_to_lists


def test_that_lists_do_not_change():
    list_a, list_b = convert_to_lists(["a"], [0, [1, 2]])
    assert list_a == ["a"]
    assert list_b == [0, [1, 2]]


def test_that_non_lists_return_lists():
    list_a, list_b = convert_to_lists(32, "34")
    assert list_a == [32]
    assert list_b == ["34"]


def test_that_partial_non_lists_return_lists():
    list_a, list_b = convert_to_lists([32], "34")
    assert list_a == [32]
    assert list_b == ["34"]


def test_that_single_non_list_return_lists():
    list_a = convert_to_lists("34")
    assert list_a == ["34"]


def test_that_single_list_return_list():
    list_a = convert_to_lists(["34"])
    assert list_a == ["34"]
