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
    Integer,
    Person,
    RegexValidator,
    ZipCode,
)

# custom Regex type for finding twitter handles.
Handle = Annotated[
    str, RegexValidator(r"@\w{1,15}", examples=["@genomoncology"])
]

# define a Pydantic class with 9 fuzzy type attributes
class Fuzzy(BaseModel):
    ascii: ASCII
    email: Email
    handle: Handle
    integer: Integer
    person: Person
    time: Datetime
    zipcode: ZipCode

# create an instance of class Fuzzy
obj = Fuzzy(
    ascii="άνθρωπος",
    email="John Doe <jdoe@example.com>",
    handle='Ian Maurer (@imaurer)',
    integer='fifty-five',
    person='mr. arthur herbert fonzarelli (fonzie)',
    time='5am on Jan 1, 2025',
    zipcode="(Zipcode: 12345-6789)",
)

# test the autocorrecting performed

# greek for man: https://en.wiktionary.org/wiki/άνθρωπος
assert obj.ascii == "anthropos"

# extract email via regular expression
assert obj.email == "jdoe@example.com"

# simple, inline regex example (see above Handle type)
assert obj.handle == "@imaurer"

# convert integer word phrase to integer value
assert obj.integer == 55

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
    "handle": "@imaurer",
    "integer": 55,
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
pip install anyascii dateparser nameparser number-parser
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
| `Integer`      | Converts numeric strings or words to integers using `number-parser`.                      |
| `Person`       | Parses person names into subfields (e.g., first, last, suffix) using `python-nameparser`. |
| `SSN`          | Extracts U.S. Social Security Numbers from strings using a regular expression.            |
| `Time`         | Converts datetime strings to `datetime` objects using `dateparser`.                       |
| `Zipcode`      | Extracts U.S. ZIP codes (5 or 9 digits) from strings using a regular expression.          |

These usable types provide a wide range of commonly needed data validations and transformations, making it
easier to work with various data formats and perform tasks like parsing, extraction, and matching.



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
pip install anyascii dateparser nameparser number-parser
```


| Fuzz Type         | Library                                                                  | License    | Purpose                                                    |
|-------------------|--------------------------------------------------------------------------|------------|------------------------------------------------------------|
| ASCII             | [anyascii](https://github.com/anyascii/anyascii)                         | ISC        | Converting Unicode into ASCII equivalents (not GPL)        |
| ASCII             | [unidecode](https://github.com/avian2/unidecode)                         | GPL        | Converting Unicode into ASCII equivalents (better quality) |
| Date              | [dateparser](https://github.com/scrapinghub/dateparser)                  | BSD-3      | Parsing dates from strings                                 |
| Integer           | [number-parser](https://github.com/scrapinghub/number-parser)            | BSD-3      | Parsing numbers from strings                               |
| Person            | [nameparser](https://github.com/derek73/python-nameparser)               | LGPL       | Parsing person names                                       |


## Creating Custom Types

FuzzTypes provides a set of base types that you can use to create
your own custom annotation types. These base types offer different
capabilities and can be extended to suit your specific data validation
and normalization needs.

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


## Maintainer

FuzzTypes was created by [Ian Maurer](https://x.com/imaurer), the CTO of [GenomOncology](https://genomoncology.com).

This MIT-based open-source project was extracted from our product which includes the ability to normalize biomedical
data for use in precision oncology clinical decision support systems. Contact me to learn more about our product
offerings.

