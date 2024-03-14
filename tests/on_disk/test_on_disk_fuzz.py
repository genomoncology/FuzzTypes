import os
import tantivy
from fuzztypes import Fuzzmoji, const


def test_tantivy():
    # make sure the index is built
    assert Fuzzmoji("balloon") == "🎈"

    # standard schema
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_integer_field("doc_id", stored=True)
    schema_builder.add_text_field("term", stored=True)
    schema = schema_builder.build()

    # create the index
    path = os.path.join(const.OnDiskPath, "Fuzzmoji.lance/_indices/tantivy")
    index = tantivy.Index(schema, path=path)
    searcher = index.searcher()

    # todo: fuzzy field not in current version
    # https://github.com/quickwit-oss/tantivy-py/issues/20
    # https://docs.rs/tantivy/latest/tantivy/query/struct.FuzzyTermQuery.html
    # index.parse_query("thought", fuzzy_fields={"term": (True, 1, False)})

    # query the index
    query = index.parse_query("thought bubble")
    result = searcher.search(query, 5)

    # check the results
    terms = []
    for score, address in result.hits:
        doc = searcher.doc(address)
        terms.extend(doc["term"])

    assert "thought balloon" in terms
    assert ":bubble_tea:" in terms


def test_fuzzmoji():
    assert Fuzzmoji("thought bubble") == "💭"
    assert Fuzzmoji("bubble team") == "🧋"
