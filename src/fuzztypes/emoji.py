from typing import List

from fuzztypes import NamedEntity, EntitySource, InMemory, OnDisk, flags


def load_emoji_entities() -> List[NamedEntity]:
    try:
        # Note: nameparser is an BSD licensed optional dependency.
        # You must import it yourself to use this functionality.
        # https://github.com/carpedm20/emoji/
        import emoji
    except ImportError:
        raise RuntimeError("Import Failed: `pip install emoji`")

    mapping = {}
    emojis = emoji.unicode_codes.get_aliases_unicode_dict()
    for value, emoji in emojis.items():
        entity = mapping.get(emoji)
        if entity is None:
            entity = NamedEntity(value=emoji)
            mapping[emoji] = entity

        # aliases ':ATM_sign:' => [':ATM_sign:', 'ATM sign']
        stripped = value.strip(":")
        aliases = [value, value.strip(":").replace("_", " ")]

        # remove any duplicates
        entity.aliases = list(set(entity.aliases + aliases))

    return list(mapping.values())


EmojiSource = EntitySource(load_emoji_entities)
Emoji = InMemory(EmojiSource, tiebreaker_mode="lesser")
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
