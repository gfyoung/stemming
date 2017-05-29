from stemming.stemming import get_top_stems


def test_top_stems():
    stem_mappings = {"stem1": [1, 2], "stem2": [4, 3, 2]}
    expected = ["stem2", "stem1"]

    actual = get_top_stems(stem_mappings)
    assert actual == expected

    stem_mappings = {"stem{i}".format(i=i): ["a"] * i for i in range(26)}
    expected = ["stem{i}".format(i=i) for i in range(25, 0, -1)]

    actual = get_top_stems(stem_mappings)
    assert actual == expected

    stem_mappings = {"stem{i}".format(i=i): ["a"] * i for i in range(26)}
    stem_mappings["stem0"] = ["a"]  # now tied for 25th place

    expected = ["stem{i}".format(i=i) for i in range(25, -1, -1)]

    actual = get_top_stems(stem_mappings)
    assert actual == expected
