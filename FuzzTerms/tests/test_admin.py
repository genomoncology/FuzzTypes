from fuzzterms import loader


def test_upsert_entities(admin, data_path):
    entities = loader.from_file(data_path / "myths.tsv")
    assert len(entities) == 5

    assert admin.stats().model_dump() == {
        "entities": 0,
        "terms": 0,
    }

    admin.upsert(entities)

    assert admin.stats().model_dump() == {
        "entities": 5,
        "terms": 12,  # 7 aliases
    }
