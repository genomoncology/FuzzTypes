def test_searcher_search(searcher, entities):
    results = searcher.search(query="athena", limit=2)
    assert list(results) == [3, "Athena", -2.1338763047496614]

    results = searcher.search(query="zeu", limit=2)
    assert list(results) == [6, "Zeus", -2.635964847043699]
