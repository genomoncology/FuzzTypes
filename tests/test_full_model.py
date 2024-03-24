from datetime import datetime
from typing import Annotated

from pydantic import BaseModel

from fuzztypes import (
    ASCII,
    Datetime,
    Email,
    Fuzzmoji,
    InMemory,
    Integer,
    Person,
    RegexValidator,
    ZipCode,
    flags,
)

# define a source, see EntitySource for using TSV, CSV, JSONL
inventors = ["Ada Lovelace", "Alan Turing", "Claude Shannon"]

# define a named entity type in memory. use OnDisk for larger data sets.
Inventor = Annotated[str, InMemory(inventors, search_flag=flags.FuzzSearch)]

# custom Regex type for finding twitter handles.
Handle = Annotated[
    str, RegexValidator(r"@\w{1,15}", examples=["@genomoncology"])
]


# define a Pydantic class with 9 fuzzy type attributes
class Fuzzy(BaseModel):
    ascii: ASCII
    email: Email
    emoji: Fuzzmoji
    handle: Handle
    integer: Integer
    inventor: Inventor
    person: Person
    time: Datetime
    zipcode: ZipCode


def test_full_model():
    # create an instance of class Fuzzy
    obj = Fuzzy(
        ascii="άνθρωπος",
        email="John Doe <jdoe@example.com>",
        emoji="thought bubble",
        handle="Ian Maurer (@imaurer)",
        integer="fifty-five",  # type: ignore[arg-type]
        inventor="ada luvlace",  # type: ignore[arg-type]
        person="mr. arthur h. fonzarelli (fonzie)",  # type: ignore[arg-type]
        time="5am on Jan 1, 2025",  # type: ignore[arg-type]
        zipcode="(Zipcode: 12345-6789)",
    )

    # test the autocorrecting performed

    # greek for man: https://en.wiktionary.org/wiki/άνθρωπος
    assert obj.ascii == "anthropos"

    # extract email via regular expression
    assert obj.email == "jdoe@example.com"

    # fuzzy match "thought bubble" to "thought balloon" emoji
    assert obj.emoji == "💭"

    # simple, inline regex example (see above Handle type)
    assert obj.handle == "@imaurer"

    # convert integer word phrase to integer value
    assert obj.integer == 55

    # case-insensitive fuzzy match on lowercase, misspelled name
    assert obj.inventor == "Ada Lovelace"

    # human name parser (title, first, middle, last, suffix, nickname)
    assert str(obj.person) == "Mr. Arthur H. Fonzarelli (fonzie)"
    assert obj.person.short_name == "Arthur Fonzarelli"
    assert obj.person.nickname == "fonzie"
    assert obj.person.last == "Fonzarelli"

    # convert time phrase to datetime object
    assert obj.time.isoformat() == "2025-01-01T05:00:00"

    # extract zip5 or zip9 formats using regular expressions
    assert obj.zipcode == "12345-6789"

    # print JSON on success
    assert obj.model_dump() == {
        "ascii": "anthropos",
        "email": "jdoe@example.com",
        "emoji": "💭",
        "handle": "@imaurer",
        "integer": 55,
        "inventor": "Ada Lovelace",
        "person": {
            "first": "Arthur",
            "init_format": "{first} {middle} {last}",
            "last": "Fonzarelli",
            "middle": "H.",
            "name_format": "{title} {first} {middle} {last} {suffix} "
            "({nickname})",
            "nickname": "fonzie",
            "suffix": "",
            "title": "Mr.",
        },
        "time": datetime(2025, 1, 1, 5),
        "zipcode": "12345-6789",
    }


def test_json_schema():
    data = Fuzzy.model_json_schema()
    expected_data = {
        "$defs": {
            "PersonModel": {
                "properties": {
                    "first": {
                        "default": "",
                        "title": "First",
                        "type": "string",
                    },
                    "init_format": {
                        "default": "{first} " "{middle} " "{last}",
                        "title": "Init " "Format",
                        "type": "string",
                    },
                    "last": {"default": "", "title": "Last", "type": "string"},
                    "middle": {
                        "default": "",
                        "title": "Middle",
                        "type": "string",
                    },
                    "name_format": {
                        "default": "{title} "
                        "{first} "
                        "{middle} "
                        "{last} "
                        "{suffix} "
                        "({nickname})",
                        "title": "Name " "Format",
                        "type": "string",
                    },
                    "nickname": {
                        "default": "",
                        "title": "Nickname",
                        "type": "string",
                    },
                    "suffix": {
                        "default": "",
                        "title": "Suffix",
                        "type": "string",
                    },
                    "title": {
                        "default": "",
                        "title": "Title",
                        "type": "string",
                    },
                },
                "title": "PersonModel",
                "type": "object",
            }
        },
        "properties": {
            "ascii": {"title": "Ascii", "type": "string"},
            "email": {
                "examples": ["user@example.com"],
                "title": "Email",
                "type": "string",
            },
            "emoji": {"title": "Emoji", "type": "string"},
            "handle": {
                "examples": ["@genomoncology"],
                "title": "Handle",
                "type": "string",
            },
            "integer": {"title": "Integer", "type": "integer"},
            "inventor": {"title": "Inventor", "type": "string"},
            "person": {"$ref": "#/$defs/PersonModel"},
            "time": {"format": "date-time", "title": "Time", "type": "string"},
            "zipcode": {
                "examples": ["12345", "12345-6789"],
                "title": "Zipcode",
                "type": "string",
            },
        },
        "required": [
            "ascii",
            "email",
            "emoji",
            "handle",
            "integer",
            "inventor",
            "person",
            "time",
            "zipcode",
        ],
        "title": "Fuzzy",
        "type": "object",
    }
    assert data == expected_data