"""
Inspired by Simon Willison's twitter post:
https://x.com/simonw/status/1766847300310028698

Collected tags from his website here:
https://simonwillison.net/tags/

Future Goal: Move to OnDisk implementation with NotFound=Allow where the
tags are added to the database incrementally for future fuzzy matching.
https://github.com/quickwit-oss/tantivy-py/issues/20
https://docs.rs/tantivy/latest/tantivy/query/struct.FuzzyTermQuery.html
"""
from typing import List

from pydantic import BaseModel
from pytest import fixture

from fuzztypes import EntitySource, InMemory, flags


@fixture(scope="session")
def TagSource(data_path):
    source = EntitySource(data_path / "simonw_tags.csv")
    assert len(source) == 1500
    return source


@fixture(scope="session")
def Tag(TagSource):
    return InMemory(
        TagSource,
        notfound_mode="allow",
        search_flag=flags.FuzzSearch,
        min_similarity=50.0,
        fuzz_scorer="QRatio",
    )


def test_fuzzy_tags_priority(Tag):
    # exact matches
    # priority is topic prevalence, higher wins.
    assert Tag["2d"].priority == 3
    assert Tag["3d"].priority == 14

    # if min_similarity <= 50.0, then chooses higher priority
    assert Tag("4d") == "3d"


def test_fuzzy_scoring_edge_cases(Tag):
    assert Tag("prompt_injection") == "promptinjection"
    assert Tag("promptinjections") == "promptinjection"
    assert Tag("prompt injections") == "promptinjection"


def test_as_a_list_of_tags(Tag):
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
