from pydantic import BaseModel

from fuzztypes.ext.emoji import Emoji, FuzzEmoji


def test_key_access():
    assert Emoji.get_value("balloon") == "🎈"
    assert Emoji.get_value(":atm_sign:") == "🏧"
    assert Emoji.get_value("atm sign") == "🏧"
    assert Emoji.get_value("atm") == "🏧"
    assert Emoji.get_value("United States") == "🇺🇸"


def test_class_resolve():
    class MyClass(BaseModel):
        emoji: Emoji = None
        fuzzy: FuzzEmoji = None

    assert MyClass(emoji="💪").emoji == "💪"
    assert MyClass(emoji=":farmer:").emoji == "🧑\u200d🌾"
    assert MyClass(emoji="farmer").emoji == "🧑‍🌾"
    assert MyClass(emoji="atm").emoji == "🏧"
    assert MyClass(emoji="atm sign").emoji == "🏧"

    assert MyClass(fuzzy="sign: atm").fuzzy == "🏧"
    assert MyClass(fuzzy="family man boy boy").fuzzy == "👨‍👦‍👦"
