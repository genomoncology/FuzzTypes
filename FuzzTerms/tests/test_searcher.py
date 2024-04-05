def test_hybrid_search(searcher, load_myths):
    assert load_myths == 5
    results = searcher.hybrid_search(query="Athena", limit=5)
    assert dict(results[0]) == {
        "name": "Athena",
        "label": "NULL",
        "priority": None,
        "meta": '{"dominion": "Wisdom"}',
        "aliases": '["Minerva","Pallas"]',
        "term": "Athena",
        "vss_distance": 0.0,
        "vss_rank": 1,
        "fts_distance": -2.1338763047496614,
        "fts_rank": 1,
    }

    results = searcher.hybrid_search(query="Herakles", limit=5)
    assert dict(results[0]) == {
        "aliases": '["Heracles"]',
        "fts_distance": 999999,
        "fts_rank": 999999,
        "label": "NULL",
        "meta": '{"dominion": "Strength"}',
        "name": "Hercules",
        "priority": None,
        "term": "Heracles",
        "vss_distance": 47.091766357421875,
        "vss_rank": 1,
    }
