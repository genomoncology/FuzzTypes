from fuzzterms import loader


def test_upserted_entities_stats(admin, entities):
    assert len(entities) == 5
    assert admin.stats().model_dump() == {
        "entities": 5,
        "terms": 12,  # 7 aliases
    }
