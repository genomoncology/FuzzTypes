from fuzzterms import Collection, encoders


def test_default_collection(collection: Collection):
    assert collection.config.search_flag.is_name
    assert collection.config.search_flag.is_alias
    assert collection.config_path.name.endswith("terms.json")
    assert collection.config_path.exists()
    assert isinstance(collection.encoder, encoders.SBertEncoder)
