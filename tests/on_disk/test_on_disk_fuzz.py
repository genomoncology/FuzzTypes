import pytest
import os

import tantivy  # type: ignore

from fuzztypes import Fuzzmoji, const, find_matches, validate_python


def test_tantivy():
    # make sure the index is built
    assert validate_python(Fuzzmoji, "balloon") == "🎈"

    # standard schema
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_integer_field("doc_id", stored=True)
    schema_builder.add_text_field("term", stored=True)
    schema = schema_builder.build()

    # create the index
    path = os.path.join(
        const.StoredValidatorPath, "Fuzzmoji.lance/_indices/tantivy"
    )
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
    assert validate_python(Fuzzmoji, "thought bubble") == "💭"
    assert validate_python(Fuzzmoji, "bubble team") == "🧋"


def test_find_matches():
    matches = find_matches(Fuzzmoji, "thought bubble")
    assert len(matches) == 10
    best = matches[0]
    assert best.key == "thought bubble"
    assert best.entity.value == "💭"
    assert best.entity.aliases == [":thought_balloon:", "thought balloon"]
    assert best.is_alias is True
    assert best.key == "thought bubble"
    assert best.score == pytest.approx(9.583168)
    assert best.term == ":thought_balloon:"
