"""
Inspired by Simon Willison's twitter post:
https://x.com/simonw/status/1766847300310028698

Collected tags from his website here:
https://simonwillison.net/tags/

Future Goal: Move to OnDiskValidator implementation with NotFound=Allow where the
tags are added to the database incrementally for future fuzzy matching.
https://github.com/quickwit-oss/tantivy-py/issues/20
https://docs.rs/tantivy/latest/tantivy/query/struct.FuzzyTermQuery.html
"""
from typing import Annotated, List

from pydantic import BaseModel
from pytest import fixture

from fuzztypes import (
    EntitySource,
    InMemoryValidator,
    flags,
    resolve_entity,
    validate_python,
    Entity,
)


@fixture(scope="session")
def TagSource(data_path):
    source = EntitySource(data_path / "simonw_tags.csv")
    assert len(source) == 1500
    return source


@fixture(scope="session")
def Tag(TagSource):
    # allow set will pass through any not founds
    # Fuzz Search using RapidFuzz
    # min_similarity is very low for demo
    # QRatio used because tags are single "words" (e.g. sqlinjection)

    return Annotated[
        str,
        InMemoryValidator(
            TagSource,
            notfound_mode="allow",
            search_flag=flags.FuzzSearch,
            min_similarity=50.0,
            fuzz_scorer="QRatio",
        ),
    ]


def test_get_entity_from_annotation(Tag):
    entity = resolve_entity(Tag, "2d")
    assert isinstance(entity, Entity)
    assert entity.priority == 3

    entity = resolve_entity(Tag, "3d")
    assert isinstance(entity, Entity)
    assert entity.priority == 14


def test_fuzzy_tags_priority(Tag):
    # since min_similarity is 50.0, it chooses higher priority
    assert validate_python(Tag, "4d") == "3d"

    # matches because 67% ratio > 50.0 minimum
    assert validate_python(Tag, "27d") == "2d"

    # less than 50% similarity is passed through (notfound_mode="allow")
    assert validate_python(Tag, "17d") == "17d"

    # different
    assert validate_python(Tag, "18d") == "i18n"

    # todo: collect allowed tags and use for future fuzzy matching
    # assert validate_python(Tag, "15d") == "17d"
    assert validate_python(Tag, "15d") == "15d"


def test_fuzzy_scoring_edge_cases(Tag):
    assert validate_python(Tag, "prompt_injection") == "promptinjection"
    assert validate_python(Tag, "promptinjections") == "promptinjection"
    assert validate_python(Tag, "prompt injections") == "promptinjection"


def test_as_a_list_of_tags(TagSource):
    Tag = Annotated[
        str,
        InMemoryValidator(
            TagSource,
            notfound_mode="allow",
            search_flag=flags.FuzzSearch,
            min_similarity=50.0,
            fuzz_scorer="QRatio",
        ),
    ]

    class Post(BaseModel):
        text: str
        tags: List[Tag]

    post = Post(
        text="Prompt injection is unsolved still.",
        tags=["prompt_injection", "AI"],
    )

    assert post.tags == ["promptinjection", "ai"]

    json = post.model_dump_json()
    second = Post.model_validate_json(json)
    assert second.tags == ["promptinjection", "ai"]
