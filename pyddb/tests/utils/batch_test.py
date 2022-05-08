from pyddb.utils.batch import batch

test_list = [0, 1, 2, 3, 4, 5, 6, 7]


def test_batch():
    new_lists = list(batch(test_list, 3))
    assert new_lists == [[0, 1, 2], [3, 4, 5], [6, 7]]
