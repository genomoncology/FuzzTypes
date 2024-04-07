from fuzzterms import Admin, databases


def test_stats(collection):
    admin = Admin(collection)
    assert admin.stats() == {
        "entities": 5,
        "terms": 12,
    }
