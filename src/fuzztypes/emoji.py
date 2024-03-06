from typing import List

from fuzztypes import NamedEntity, EntitySource, InMemory, const, flags


def load_emoji_entities() -> List[NamedEntity]:
    try:
        # Note: nameparser is an BSD licensed optional dependency.
        # You must import it yourself to use this functionality.
        # https://github.com/carpedm20/emoji/
        import emoji
    except ImportError:  # pragma: no cover
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
FuzzEmoji = InMemory(
    EmojiSource,
    search_mode=flags.FuzzSearch,
    tiebreaker_mode="lesser",
)
Vibemoji = InMemory(
    EmojiSource,
    search_mode=flags.SemanticSearch,
    tiebreaker_mode="lesser",
    sem_min_score=10.0,
)
