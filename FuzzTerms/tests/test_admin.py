def test_upserted_entities_stats(admin, load_myths):
    assert load_myths == 5
    assert admin.stats() == {
        "entities": 5,
        "terms": 12,  # 7 aliases
    }
