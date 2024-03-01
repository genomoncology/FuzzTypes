from typing import List

from fuzztype import AliasStr, NamedEntity, EntitySource, FuzzStr


def load_emoji_entities() -> List[NamedEntity]:
    try:
        import emoji
    except ImportError:  # pragma: no cover
        raise RuntimeError("Import Failed: `pip install emoji`")

    mapping = {}
    emojis = emoji.unicode_codes.get_aliases_unicode_dict()
    for name, emoji in emojis.items():
        entity = mapping.get(emoji)
        if entity is None:
            entity = NamedEntity(name=emoji)
            mapping[emoji] = entity

        # aliases ':ATM_sign:' => [':ATM_sign:', 'ATM sign']
        stripped = name.strip(":")
        aliases = [name, name.strip(":").replace("_", " ")]

        # remove any duplicates
        entity.aliases = list(set(entity.aliases + aliases))

    return list(mapping.values())


EmojiSource = EntitySource(load_emoji_entities)
Emoji = AliasStr(EmojiSource, tiebreaker_mode="alphabetical")
FuzzEmoji = FuzzStr(EmojiSource, tiebreaker_mode="alphabetical")
