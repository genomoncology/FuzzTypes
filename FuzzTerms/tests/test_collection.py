from fuzzterms import Collection


def test_default_collection(collection: Collection):
    assert collection.config.search_type_default_flag.is_name
    assert collection.config.search_type_default_flag.is_alias
