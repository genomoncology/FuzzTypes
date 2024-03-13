from typing import List

from fuzztypes import NamedEntity, EntitySource, OnDisk, flags, lazy


def load_emoji_entities() -> List[NamedEntity]:
    get_aliases_unicode_dict = lazy.lazy_import(
        "emoji.unicode_codes", "get_aliases_unicode_dict"
    )

    mapping = {}
    emoji_mapping = get_aliases_unicode_dict()
    for value, emoji in emoji_mapping.items():
        entity = mapping.get(emoji)
        if entity is None:
            entity = NamedEntity(value=emoji)
            mapping[emoji] = entity

        # aliases ':ATM_sign:' => [':ATM_sign:', 'ATM sign']
        aliases = [value, value.strip(":").replace("_", " ")]

        # remove any duplicates
        entity.aliases = list(set(entity.aliases + aliases))

    return list(mapping.values())


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
