from fuzztypes import Emoji, emojis


def test_key_access():
    assert Emoji("balloon") == "🎈"
    assert Emoji(":atm_sign:") == "🏧"
    assert Emoji("atm sign") == "🏧"
    assert Emoji("atm") == "🏧"
    assert Emoji("United States") == "🇺🇸"


def test_load_emojis():
    entities = emojis.load_emoji_entities()
    assert len(entities) > 2000
    assert entities[0].value == "🥇"
    assert set(entities[0].aliases) == {"1st place medal", ":1st_place_medal:"}
