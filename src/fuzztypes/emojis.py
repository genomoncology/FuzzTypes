from collections import defaultdict
from typing import List
from pydantic import TypeAdapter

from fuzztypes import NamedEntity, EntitySource, OnDisk, flags, lazy


def load_emoji_entities() -> List[NamedEntity]:
    get_aliases_unicode_dict = lazy.lazy_import(
        "emoji.unicode_codes", "get_aliases_unicode_dict"
    )

    mapping = defaultdict(list)
    emoji_mapping = get_aliases_unicode_dict()
    for value, emoji in emoji_mapping.items():
        mapping[emoji].extend([value, value.strip(":").replace("_", " ")])

    data = ({"value": k, "aliases": v} for k, v in mapping.items())
    return TypeAdapter(List[NamedEntity]).validate_python(data)


EmojiSource = EntitySource(load_emoji_entities)

Emoji = OnDisk(
    "Emoji",
    EmojiSource,
    search_flag=flags.AliasSearch,
    tiebreaker_mode="lesser",
)

Fuzzmoji = OnDisk(
    "Fuzzmoji",
    EmojiSource,
    search_flag=flags.FuzzSearch,
    tiebreaker_mode="lesser",
    min_similarity=10.0,
    device="cpu",
)

Vibemoji = OnDisk(
    "Vibemoji",
    EmojiSource,
    search_flag=flags.SemanticSearch,
    tiebreaker_mode="lesser",
    min_similarity=10.0,
    device="cpu",
)
