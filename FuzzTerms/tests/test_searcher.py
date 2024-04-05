def test_hybrid_search(searcher, entities):
    results = searcher.hybrid_search(query="Athena", limit=5)
    print("Athena search =>")
    for result in results:
        print(dict(result))
    print("done.")

    results = searcher.hybrid_search(query="Herakles", limit=5)
    print("Quicksilver search =>")
    for result in results:
        print(dict(result))
    print("done.")
