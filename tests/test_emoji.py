from fuzztypes import Emoji


def test_key_access():
    assert Emoji.get_value("balloon") == "🎈"
    assert Emoji.get_value(":atm_sign:") == "🏧"
    assert Emoji.get_value("atm sign") == "🏧"
    assert Emoji.get_value("atm") == "🏧"
    assert Emoji.get_value("United States") == "🇺🇸"
