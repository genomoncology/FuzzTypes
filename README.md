# FuzzTypes

FuzzTypes is a set of "autocorrecting" annotation types that expands
upon [Pydantic](https://github.com/pydantic/pydantic)'s included [data
conversions.](https://docs.pydantic.dev/latest/concepts/conversion_table/)
Designed for simplicity, it provides powerful normalization capabilities
(e.g. named entity linking) to ensure structured data is composed of
"smart things" not "dumb strings".

*Note: FuzzTypes is currently experimental and there could be breaking
changes to it's API over the next few weeks.*

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
from pydantic import BaseModel
from fuzztypes import (
    ASCII,
    Datetime,
    Email,
    Fuzzmoji,
    InMemory,
    Integer,
    Person,
    Regex,
    ZipCode,
    flags,
)

# define a source, see EntitySource for using TSV, CSV, JSONL
inventors = ["Ada Lovelace", "Alan Turing", "Claude Shannon"]

# define a named entity type in memory. use OnDisk for larger data sets.
Inventor = InMemory(inventors, search_flag=flags.FuzzSearch)

# custom Regex type for finding twitter handles.
Handle =  Regex(r'@\w{1,15}', examples=["@genomoncology"])

# define a Pydantic class with 9 fuzzy type attriubutes
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
assert str(obj.person) == 'Mr. Arthur Herbert Fonzarelli (fonzie)'
assert obj.person.short_name == "Arthur Fonzarelli"
assert obj.person.nickname == "fonzie"
assert obj.person.last == "Fonzarelli"

# convert time phrase to datetime object
assert obj.time.isoformat() == "2025-01-01T05:00:00"

# extract zip5 or zip9 formats using regular expressions
assert obj.zipcode == "12345-6789"

# print JSON on success
print(obj.model_dump_json(indent=4))
```

Types can also be used outside of Pydantic models to validate and normalize data:

```python
from fuzztypes import Date, Fuzzmoji

# access value via "call" (parenthesis)
assert Date("1 JAN 2023").isoformat() == "2023-01-01"
assert Fuzzmoji("tada") == '🎉'

# access entity via "key lookup" (square brackets)
assert Fuzzmoji["movie cam"].value == "🎥"
assert Fuzzmoji["movie cam"].aliases == [':movie_camera:', 'movie camera']
assert Fuzzmoji["movie cam"].model_dump() == {
    'value': '🎥',
    'label': None,
    'meta': None,
    'priority': None,
    'aliases': [':movie_camera:', 'movie camera']
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


## Base Types

Base types are the fundamental building blocks in FuzzTypes. They provide the core functionality and can be used to
create custom annotation types tailored to specific use cases.

| Type       | Description                                                                                |
|------------|--------------------------------------------------------------------------------------------|
| `DateType` | Base type for fuzzy parsing date objects.                                                  |
| `Function` | Allows using any function that accepts one value and returns one value for transformation. |
| `InMemory` | Enables matching entities in memory using exact, alias, fuzzy, or semantic search.         |
| `OnDisk`   | Performs matching entities stored on disk using exact, alias, fuzzy, or semantic search.   |
| `Regex`    | Allows matching values using a regular expression pattern.                                 |
| `TimeType` | Base type for fuzzy parsing datetime objects (e.g., "tomorrow at 5am").                    |

These base types offer flexibility and extensibility, enabling you to create custom annotation types that suit your
specific data validation and normalization requirements.


## Usable Types

Usable types are pre-built annotation types in FuzzTypes that can be directly used in Pydantic models. They provide
convenient and ready-to-use functionality for common data types and scenarios.

| Type        | Description                                                                               |
|-------------|-------------------------------------------------------------------------------------------|
| `ASCII`     | Converts Unicode strings to ASCII equivalents using either `anyascii` or `unidecode`.     |
| `Date`      | Converts date strings to `date` objects using `dateparser`.                               |
| `Email`     | Extracts email addresses from strings using a regular expression.                         |
| `Emoji`     | Matches emojis based on Unicode Consortium aliases using the `emoji` library.             |
| `Fuzzmoji`  | Matches emojis using fuzzy string matching against aliases.                               |
| `Integer`   | Converts numeric strings or words to integers using `number-parser`.                      |
| `Person`    | Parses person names into subfields (e.g., first, last, suffix) using `python-nameparser`. |
| `SSN`       | Extracts U.S. Social Security Numbers from strings using a regular expression.            |
| `Time`      | Converts datetime strings to `datetime` objects using `dateparser`.                       |
| `Vibemoji`  | Matches emojis using semantic similarity against aliases.                                 |
| `Zipcode`   | Extracts U.S. ZIP codes (5 or 9 digits) from strings using a regular expression.          |

These usable types provide a wide range of commonly needed data validations and transformations, making it
easier to work with various data formats and perform tasks like parsing, extraction, and matching.


## Configuring FuzzTypes

FuzzTypes provides a set of configuration options that allow you to customize the behavior of the annotation types.
These options can be passed as arguments when creating an instance of a FuzzType.

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
| `validator_mode`  | `Literal["before"]`                     | `"before"`            | The validation mode to use for Pydantic. Currently, only the "before" mode is fully tested and supported, which resolves the value before validation.                                                                                                                                                                                   |

These configuration options provide flexibility in tailoring the behavior of FuzzTypes to suit your specific use case.
By adjusting these options, you can control aspects such as case sensitivity, device selection, encoding mechanism,
search strategy, similarity thresholds, and more.


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


| Fuzz Type  | Library                                                                  | License    | Purpose                                                    |
|------------|--------------------------------------------------------------------------|------------|------------------------------------------------------------|
| ASCII      | [anyascii](https://github.com/anyascii/anyascii)                         | ISC        | Converting Unicode into ASCII equivalents (not GPL)        |
| ASCII      | [unidecode](https://github.com/avian2/unidecode)                         | GPL        | Converting Unicode into ASCII equivalents (better quality) |
| Date       | [dateparser](https://github.com/scrapinghub/dateparser)                  | BSD-3      | Parsing dates from strings                                 |
| Emoji      | [emoji](https://github.com/carpedm20/emoji/)                             | BSD        | Handling and manipulating emoji characters                 |
| Fuzz       | [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz)                      | MIT        | Performing fuzzy string matching                           |
| InMemory   | [numpy](https://numpy.org/)                                              | BSD        | Numerical computing in Python                              |
| InMemory   | [scikit-learn](https://scikit-learn.org/)                                | BSD        | Machine learning in Python                                 |
| InMemory   | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | Apache-2.0 | Encoding sentences into high-dimensional vectors           |
| Integer    | [number-parser](https://github.com/scrapinghub/number-parser)            | BSD-3      | Parsing numbers from strings                               |
| OnDisk     | [lancedb](https://github.com/lancedb/lancedb)                            | Apache-2.0 | High-performance, on-disk vector database                  |
| OnDisk     | [pyarrow](https://github.com/apache/arrow)                               | Apache-2.0 | In-memory columnar data format and processing library      |
| OnDisk     | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | Apache-2.0 | Encoding sentences into high-dimensional vectors           |
| OnDisk     | [tantivy](https://github.com/quickwit-oss/tantivy-py)                    | MIT        | Full-text search (FTS) for LanceDB.                        |
| Person     | [nameparser](https://github.com/derek73/python-nameparser)               | LGPL       | Parsing person names                                       |


## Maintainer

FuzzTypes was created by [Ian Maurer](https://x.com/imaurer), the CTO of [GenomOncology](https://genomoncology.com).

This MIT-based open-source project was extracted from our product which includes the ability to normalize biomedical
data for use in precision oncology clinical decision support systems. Contact me to learn more about our product
offerings.


## Roadmap

Additional capabilities will soon be added:

- Complete OnDisk [fuzzy string matching](https://github.com/quickwit-oss/tantivy-py/issues/20).
- Reranking models
- Hybrid search (linear and reciprocal rank fusion using fuzzy and semantic)
- Trie-based autocomplete and aho-corasick search
- `Humanize` intword and ordinals
- `Pint` quantities
- `Country` and `Currency` codes/names

The following usable types are planned for future implementation in FuzzTypes:

| Type           | Description                                                                               |
|----------------|-------------------------------------------------------------------------------------------|
| `AirportCode`  | Represents airport codes (e.g., "ORD").                                                   |
| `Airport`      | Represents airport names (e.g., "O'Hare International Airport").                          |
| `CountryCode`  | Represents ISO country codes (e.g., "US").                                                |
| `Country`      | Represents country names (e.g., "United States").                                         |
| `Currency`     | Represents currency codes (e.g., "USD").                                                  |
| `LanguageCode` | Represents ISO language codes (e.g., "en").                                               |
| `Language`     | Represents language names (e.g., "English").                                              |
| `Quantity`     | Converts strings to `Quantity` objects with value and unit using `pint`.                  |
| `URL`          | Represents normalized URLs with tracking parameters removed using `url-normalize`.        |
| `USStateCode`  | Represents U.S. state codes (e.g., "CA").                                                 |
| `USState`      | Represents U.S. state names (e.g., "California").                                         |


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

### Function Base Type

The `Function` base type allows you to use any function that accepts
one value and returns one value for transformation. It is useful
for creating simple annotation types that perform custom data
transformations.

Example:
```python
from fuzztypes import Function

# Create a custom annotation type that converts a value to uppercase
UpperCase = Function(str.upper)

class MyModel(BaseModel):
    name: UpperCase

model = MyModel(name="john")
assert model.name == "JOHN"
```

### InMemory Base Type

The `InMemory` base type enables matching entities in memory using
exact, alias, fuzzy, or semantic search. It is suitable for small
to medium-sized datasets that can fit in memory and provides fast
matching capabilities.

Example:
```python
from fuzztypes import InMemory, flags

# Create a custom annotation type for matching fruits
fruits = ["Apple", "Banana", "Orange"]
Fruit = InMemory(fruits, search_flag=flags.FuzzSearch)

class MyModel(BaseModel):
    fruit: Fruit

model = MyModel(fruit="appel")
assert model.fruit == "Apple"
```

### OnDisk Base Type

The `OnDisk` base type performs matching entities stored on disk
using exact, alias, fuzzy, or semantic search. It leverages the
LanceDB library for efficient storage and retrieval of entities.
`OnDisk` is recommended for large datasets that cannot fit in memory.

Example:
```python
from fuzztypes import OnDisk, flags

# Create a custom annotation type for matching countries
countries = ["United States", "United Kingdom", "Canada"]
Country = OnDisk("Country", countries, search_flag=flags.FuzzSearch)

class MyModel(BaseModel):
    country: Country

model = MyModel(country="USA")
assert model.country == "United States"
```

### DateType and TimeType

The `DateType` and `TimeType` base types provide fuzzy parsing
capabilities for date and datetime objects, respectively. They allow
you to define flexible date and time formats and perform parsing
based on specified settings such as date order, timezone, and
relative base.

Example:
```python
from fuzztypes import DateType, DatetimeType

# Create custom annotation types for parsing dates and times
Date = DateType(date_order="MDY")
Time = DatetimeType(timezone="UTC")

class MyModel(BaseModel):
    date: Date
    time: Time

model = MyModel(date="4/20/2023", time="10:30 PM")
print(model.date)  # Output: datetime.date(2023, 4, 20)
print(model.time)  # Output: datetime.datetime(2023, 4, 20, 22, 30, tzinfo=<UTC>)
```

### Regex

The `Regex` base type allows matching values using a regular
expression pattern. It is useful for creating annotation types that
validate and extract specific patterns from input values.

Example:
```python
from fuzztypes import Regex

# Create a custom annotation type for matching email addresses
Email = Regex(r"[\w\.-]+@[\w\.-]+\.\w+")

class MyModel(BaseModel):
    email: Email

model = MyModel(email="john.doe@example.com")
assert model.email == "john.doe@example.com"
```

