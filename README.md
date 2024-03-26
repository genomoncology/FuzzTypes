# FuzzTypes

FuzzTypes is a set of "autocorrecting" annotation types that expands
upon [Pydantic](https://github.com/pydantic/pydantic)'s included [data
conversions.](https://docs.pydantic.dev/latest/concepts/conversion_table/)
Designed for simplicity, it provides powerful normalization capabilities
(e.g. named entity linking) to ensure structured data is composed of
"smart things" not "dumb strings".


## Getting Started

Pydantic supports basic conversion of data between types. For instance:

```python
from pydantic import BaseModel

class Normal(BaseModel):
    boolean: bool
    float: float
    integer: int
    
obj = Normal(
    boolean='yes',
    float='2',
    integer='3',
)
assert obj.boolean is True
assert obj.float == 2.0
assert obj.integer == 3
```

FuzzTypes expands on the standard data conversions handled by Pydantic and
provides a variety of autocorrecting annotation types. 

```python
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel

from fuzztypes import (
    ASCII,
    Datetime,
    Email,
    Fuzzmoji,
    InMemoryValidator,
    Integer,
    Person,
    RegexValidator,
    ZipCode,
    flags,
)

# define a source, see EntitySource for using TSV, CSV, JSONL
inventors = ["Ada Lovelace", "Alan Turing", "Claude Shannon"]

# define a in memory validator with fuzz search enabled.
Inventor = Annotated[
    str, InMemoryValidator(inventors, search_flag=flags.FuzzSearch)
]

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

# create an instance of class Fuzzy
obj = Fuzzy(
    ascii="άνθρωπος",
    email="John Doe <jdoe@example.com>",
    emoji='thought bubble',
    handle='Ian Maurer (@imaurer)',
    integer='fifty-five',
    inventor='ada luvlace',
    person='mr. arthur herbert fonzarelli (fonzie)',
    time='5am on Jan 1, 2025',
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
```

## Installation

Available on [PyPI](https://pypi.org/project/FuzzTypes/):

```bash
pip install fuzztypes
```

To install all dependencies (see below), you can copy and paste this:

```bash
pip install anyascii dateparser emoji lancedb nameparser number-parser rapidfuzz sentence-transformers tantivy
```


## Google Colab Notebook

There is a read-only notebook that you can copy and edit to try out FuzzTypes:

[https://colab.research.google.com/drive/1GNngxcTUXpWDqK_qNsJoP2NhSN9vKCzZ?usp=sharing](https://colab.research.google.com/drive/1GNngxcTUXpWDqK_qNsJoP2NhSN9vKCzZ?usp=sharing)


## Base Validators

Base validators are the building blocks of FuzzTypes that can be used for creating custom "usable types".

| Type                | Description                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------|
| `DateType`          | Base date type, pass in arguments such as `date_order`, `strict` and `relative_base`.       |
| `FuzzValidator`     | Validator class that calls a provided function and handles core and json schema config.     |
| `InMemoryValidator` | Enables matching entities in memory using exact, alias, fuzzy, or semantic search.          |
| `OnDiskValidator`   | Performs matching entities stored on disk using exact, alias, fuzzy, or semantic search.    |
| `RegexValidator`    | Regular expression pattern matching base validator.                                         |
| `DatetimeType`      | Base datetime type, pass in arguments such as `date_order`, `timezone` and `relative_base`. |

These base types offer flexibility and extensibility, enabling you to create custom annotation types that suit your
specific data validation and normalization requirements.


## Usable Types

Usable types are pre-built annotation types in FuzzTypes that can be directly used in Pydantic models. They provide
convenient and ready-to-use functionality for common data types and scenarios.

| Type           | Description                                                                               |
|----------------|-------------------------------------------------------------------------------------------|
| `ASCII`        | Converts Unicode strings to ASCII equivalents using either `anyascii` or `unidecode`.     |
| `Date`         | Converts date strings to `date` objects using `dateparser`.                               |
| `Email`        | Extracts email addresses from strings using a regular expression.                         |
| `Emoji`        | Matches emojis based on Unicode Consortium aliases using the `emoji` library.             |
| `Fuzzmoji`     | Matches emojis using fuzzy string matching against aliases.                               |
| `Integer`      | Converts numeric strings or words to integers using `number-parser`.                      |
| `LanguageCode` | Resolves language to ISO language codes (e.g., "en").                                     |
| `LanguageName` | Resolves language to ISO language names (e.g., "English").                                |
| `Language`     | Resolves language to ISO language object (name, alpha_2, alpha_3, scope, type, etc.).     |
| `Person`       | Parses person names into subfields (e.g., first, last, suffix) using `python-nameparser`. |
| `SSN`          | Extracts U.S. Social Security Numbers from strings using a regular expression.            |
| `Time`         | Converts datetime strings to `datetime` objects using `dateparser`.                       |
| `Vibemoji`     | Matches emojis using semantic similarity against aliases.                                 |
| `Zipcode`      | Extracts U.S. ZIP codes (5 or 9 digits) from strings using a regular expression.          |

These usable types provide a wide range of commonly needed data validations and transformations, making it
easier to work with various data formats and perform tasks like parsing, extraction, and matching.


## InMemoryValidator and OnDiskValidator Configuration

The InMemory and OnDisk Validator objects work with lists of Entities.

The following table describes the available configuration options:

| Argument          | Type                                    | Default               | Description                                                                                                                                                                                                                                                                                                                             |
|-------------------|-----------------------------------------|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `case_sensitive`  | `bool`                                  | `False`               | If `True`, matches are case-sensitive. If `False`, matches are case-insensitive.                                                                                                                                                                                                                                                        |
| `device`          | `Literal["cpu", "cuda", "mps"]`         | `"cpu"`               | The device to use for generating semantic embeddings and LanceDB indexing. Available options are "cpu", "cuda" (for NVIDIA GPUs), and "mps" (for Apple's Metal Performance Shaders).                                                                                                                                                    |
| `encoder`         | `Union[Callable, str, Any]`             | `None`                | The encoder to use for generating semantic embeddings. It can be a callable function, a string specifying the name or path of a pre-trained model, or any other object that implements the encoding functionality.                                                                                                                      |
| `examples`        | `List[Any]`                             | `None`                | A list of example values to be used in schema generation. These examples are included in the generated JSON schema to provide guidance on the expected format of the input values.                                                                                                                                                      |
| `fuzz_scorer`     | `Literal["token_sort_ratio", ...]`      | `"token_sort_ratio"`  | The scoring algorithm to use for fuzzy string matching. Available options include "token_sort_ratio", "ratio", "partial_ratio", "token_set_ratio", "partial_token_set_ratio", "token_ratio", "partial_token_ratio", "WRatio", and "QRatio". Each algorithm has its own characteristics and trade-offs between accuracy and performance. |
| `limit`           | `int`                                   | `10`                  | The maximum number of matches to return when performing fuzzy or semantic searches.                                                                                                                                                                                                                                                     |
| `min_similarity`  | `float`                                 | `80.0`                | The minimum similarity score required for a match to be considered valid. Matches with a similarity score below this threshold will be discarded.                                                                                                                                                                                       |
| `notfound_mode`   | `Literal["raise", "none", "allow"]`     | `"raise"`             | The action to take when a matching entity is not found. Available options are "raise" (raises an exception), "none" (returns `None`), and "allow" (returns the input key as the value).                                                                                                                                                 |
| `search_flag`     | `flags.SearchFlag`                      | `flags.DefaultSearch` | The search strategy to use for finding matches. It is a combination of flags that determine which fields of the `NamedEntity` are considered for matching and whether fuzzy or semantic search is enabled. Available options are defined in the `flags` module.                                                                         |
| `tiebreaker_mode` | `Literal["raise", "lesser", "greater"]` | `"raise"`             | The strategy to use for resolving ties when multiple matches have the same similarity score. Available options are "raise" (raises an exception), "lesser" (returns the match with the lower value), and "greater" (returns the match with the greater value).                                                                          |


## Lazy Dependencies

FuzzTypes leverages several powerful libraries to extend its functionality.

These dependencies are not installed by default with FuzzTypes to keep the
installation lightweight. Instead, they are optional and can be installed
as needed depending on which types you use.

Below is a list of these dependencies, including their licenses, purpose, and what
specific Types require them.

Right now, you must pip install the modules directly, in the future you will 
be able to install them automatically as part of the main install using pip extras.

To install all dependencies, you can copy and paste this:

```bash
pip install anyascii dateparser emoji lancedb nameparser number-parser rapidfuzz sentence-transformers tantivy
```


| Fuzz Type         | Library                                                                  | License    | Purpose                                                    |
|-------------------|--------------------------------------------------------------------------|------------|------------------------------------------------------------|
| ASCII             | [anyascii](https://github.com/anyascii/anyascii)                         | ISC        | Converting Unicode into ASCII equivalents (not GPL)        |
| ASCII             | [unidecode](https://github.com/avian2/unidecode)                         | GPL        | Converting Unicode into ASCII equivalents (better quality) |
| Date              | [dateparser](https://github.com/scrapinghub/dateparser)                  | BSD-3      | Parsing dates from strings                                 |
| Emoji             | [emoji](https://github.com/carpedm20/emoji/)                             | BSD        | Handling and manipulating emoji characters                 |
| Fuzz              | [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz)                      | MIT        | Performing fuzzy string matching                           |
| InMemoryValidator | [numpy](https://numpy.org/)                                              | BSD        | Numerical computing in Python                              |
| InMemoryValidator | [scikit-learn](https://scikit-learn.org/)                                | BSD        | Machine learning in Python                                 |
| InMemoryValidator | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | Apache-2.0 | Encoding sentences into high-dimensional vectors           |
| Integer           | [number-parser](https://github.com/scrapinghub/number-parser)            | BSD-3      | Parsing numbers from strings                               |
| OnDiskValidator   | [lancedb](https://github.com/lancedb/lancedb)                            | Apache-2.0 | High-performance, on-disk vector database                  |
| OnDiskValidator   | [pyarrow](https://github.com/apache/arrow)                               | Apache-2.0 | In-memory columnar data format and processing library      |
| OnDiskValidator   | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | Apache-2.0 | Encoding sentences into high-dimensional vectors           |
| OnDiskValidator   | [tantivy](https://github.com/quickwit-oss/tantivy-py)                    | MIT        | Full-text search (FTS) for LanceDB.                        |
| Person            | [nameparser](https://github.com/derek73/python-nameparser)               | LGPL       | Parsing person names                                       |


## Maintainer

FuzzTypes was created by [Ian Maurer](https://x.com/imaurer), the CTO of [GenomOncology](https://genomoncology.com).

This MIT-based open-source project was extracted from our product which includes the ability to normalize biomedical
data for use in precision oncology clinical decision support systems. Contact me to learn more about our product
offerings.


## Structured Data Generation via LLM Function Calling and Custom GPT Actions

Several libraries (e.g. [Instructor](https://github.com/jxnl/instructor),
[Outlines](https://github.com/outlines-dev/outlines),
[Marvin](https://github.com/prefecthq/marvin)) use Pydantic to define models for structured data generation
using Large Language Models (LLMs) via function calling or a grammar/regex
based sampling approach based on the [JSON schema generated by Pydantic](https://docs.pydantic.dev/latest/concepts/json_schema/).

This approach allows for the enumeration of allowed values using
Python's `Literal`, `Enum` or JSON Schema's `examples` field directly
in your Pydantic class declaration which is used by the LLM to
generate valid values. This approach works exceptionally well for
low-cardinality (not many unique allowed values) such as the world's
continents (7 in total).

This approach, however, doesn't scale well for high-cardinality (many unique
allowed values) such as the number of known human genomic variants (~325M).
Where exactly the cutoff is between "low" and "high" cardinality is an exercise
left to the reader and their use case.

That's where FuzzTypes come in. The allowed values are managed by the FuzzTypes
annotations and the values are resolved during the Pydantic validation process.
This can include fuzzy and semantic searching that throws an exception if the
provided value doesn't meet a minimum similarity threshold defined by the
developer.

Errors discovered via Pydantic can be caught and resubmitted to the LLM for
correction. The error will contain examples, expected patterns, and closest
matches to help steer the LLM to provide a better informed guess.


## Creating Custom Types

FuzzTypes provides a set of base types that you can use to create
your own custom annotation types. These base types offer different
capabilities and can be extended to suit your specific data validation
and normalization needs.

### EntitySource

FuzzTypes provides the `EntitySource` class to manage and load
entity data from various sources. It supports JSON Lines (`.jsonl`),
CSV (`.csv`), TSV (`.tsv`), and Text (`.txt`) formats, as well as
loading entities from a callable function.

Example:
```python
from pathlib import Path
from fuzztypes import EntitySource, NamedEntity

# Load entities from a CSV file
fruit_source = EntitySource(Path("path/to/fruits.csv"))

# Load entities from a callable function
def load_animals():
    return [
        NamedEntity(value="Dog", aliases=["Canine"]),
        NamedEntity(value="Cat", aliases=["Feline"]),
    ]

animal_source = EntitySource(load_animals)
```

### InMemoryValidator Base Type

The `InMemoryValidator` base type enables matching entities in memory using
exact, alias, fuzzy, or semantic search. It is suitable for small
to medium-sized datasets that can fit in memory and provides fast
matching capabilities.

Example:
```python
from typing import Annotated
from pydantic import BaseModel
from fuzztypes import InMemoryValidator, flags

# Create a custom annotation type for matching fruits
fruits = ["Apple", "Banana", "Orange"]
Fruit = Annotated[
    str, InMemoryValidator(fruits, search_flag=flags.FuzzSearch)
]

class MyModel(BaseModel):
    fruit: Fruit

model = MyModel(fruit="appel")
assert model.fruit == "Apple"
```

### OnDiskValidator Base Type

The `OnDiskValidator` base type performs matching entities stored on disk
using exact, alias, fuzzy, or semantic search. It leverages the
LanceDB library for efficient storage and retrieval of entities.
`OnDiskValidator` is recommended for large datasets that cannot fit in memory.

Example:
```python
from typing import Annotated
from pydantic import BaseModel
from fuzztypes import OnDiskValidator

# Create a custom annotation type for matching countries stored on disk
countries = [
    ("United States", "US"),
    ("United Kingdom", "UK"),
    ("Canada", "CA"),
]
Country = Annotated[str, OnDiskValidator("Country", countries)]

class MyModel(BaseModel):
    country: Country

assert MyModel(country="Canada").country == "Canada"
assert MyModel(country="US").country == "United States"
```

### DateType and TimeType

The `DateValidator` and `DatetimeValidator` base types provide fuzzy parsing
capabilities for date and datetime objects, respectively. They allow
you to define flexible date and time formats and perform parsing
based on specified settings such as date order, timezone, and
relative base.

Example:

```python
from datetime import date, datetime
from pydantic import BaseModel
from typing import Annotated
from fuzztypes import DateValidator, DatetimeValidator

MyDate = Annotated[date, DateValidator(date_order="MDY")]
MyTime = Annotated[datetime, DatetimeValidator(timezone="UTC")]

class MyModel(BaseModel):
    date: MyDate
    time: MyTime

model = MyModel(date="1/1/2023", time="1/1/23 at 10:30 PM")
assert model.date.isoformat() == "2023-01-01"
assert model.time.isoformat() == "2023-01-01T22:30:00+00:00"
```


### FuzzValidator

The `FuzzValidator` is the base of the fuzztypes typing system.
It can be used directly to wrap any python function.

Example:
```python
from typing import Annotated
from pydantic import BaseModel
from fuzztypes import FuzzValidator

# Create a custom annotation type that converts a value to uppercase
UpperCase = Annotated[str, FuzzValidator(str.upper)]

class MyModel(BaseModel):
    name: UpperCase

model = MyModel(name="john")
assert model.name == "JOHN"
```


### Regex

The `Regex` base type allows matching values using a regular
expression pattern. It is useful for creating annotation types that
validate and extract specific patterns from input values.

Example:
```python
from typing import Annotated
from pydantic import BaseModel
from fuzztypes import RegexValidator

# Create a custom annotation type for matching email addresses
IPAddress = Annotated[
    str, RegexValidator(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
]

class MyModel(BaseModel):
    ip_address: IPAddress

model = MyModel(ip_address="My internet IP address is 192.168.127.12")
assert model.ip_address == "192.168.127.12"
```

### Languages

Languages are loaded from the [Debian iso-codes](https://salsa.debian.org/iso-codes-team/iso-codes/) project.

Languages are resolved using their preferred, common, inverted, bibliographic name, or 2 or 3 letter alpha code.

Languages can be included as a string name (LanguageName), string code (LanguageCode) or full language object.

The preferred code is the 2 letter version and will be used if available. Otherwise, the 3 letter alpha code is used.

Example:

```python
from pydantic import BaseModel
from fuzztypes import (
    Language,
    LanguageName,
    LanguageCode,
    LanguageScope,
    LanguageType,
    LanguageNamedEntity,
    validate_python,
)
class Model(BaseModel):
    language_code: LanguageCode
    language_name: LanguageName
    language: Language

# Test that Language resolves to the complete language object
data = dict(language_code="en", language="English", language_name="ENG")
obj = validate_python(Model, data)
assert obj.language_code == "en"
assert obj.language_name == "English"
assert obj.language.scope == LanguageScope.INDIVIDUAL
assert obj.language.type == LanguageType.LIVING
assert isinstance(obj.language, LanguageNamedEntity)
assert obj.model_dump(exclude_defaults=True, mode="json") == {
    "language": {
        "aliases": ["en", "eng"],
        "alpha_2": "en",
        "alpha_3": "eng",
        "scope": "I",
        "type": "L",
        "value": "English",
    },
    "language_code": "en",
    "language_name": "English",
}
```

### Validate Python and JSON functions

Functional approach to validating python and json are available.
Below are examples for the `validate_python` and `validate_json` functions:

```python
from pydantic import BaseModel
from fuzztypes import validate_python, validate_json, Integer, Date

# validate python
assert validate_python(Integer, "two hundred") == 200

# validate json
class MyModel(BaseModel):
    date: Date

json = '{"date": "July 4th 2021"}'
obj = validate_json(MyModel, json)
assert obj.date.isoformat() == "2021-07-04"
```

### Resolve Entities from FuzzValidator or Annotation

Entities can be resolved from the `FuzzValidator` validators such as InMemoryValidator
or OnDiskValidator or the defined `Annotation` type using the `resolve_entity` function:

```python
from typing import Annotated
from fuzztypes import resolve_entity, InMemoryValidator

elements = ["earth", "fire", "water", "air"]
ElementValidator = InMemoryValidator(elements)
Element = Annotated[str, ElementValidator]

assert resolve_entity(ElementValidator, "EARTH").model_dump() == {
    "aliases": [],
    "label": None,
    "meta": None,
    "priority": None,
    "value": "earth",
}

assert resolve_entity(Element, "Air").model_dump(
    exclude_defaults=True
) == {"value": "air"}
```