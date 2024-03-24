__version__ = "0.0.2"

# logging
import logging

logger = logging.getLogger("fuzztypes")
logger.setLevel(logging.WARNING)

# flags and constants
from . import flags
from . import const

# utilities
from . import utils
from . import lazy

# Validation
from .validation import (
    FuzzValidator,
    validate_python,
    validate_json,
    get_type_adapter,
)

# Schema
from .entity import Entity, NamedEntity, EntitySource
from .match import Match, MatchResult, Record

# Hidden Abstract Types
from . import abstract
from . import storage

# Base Named Entity Types
from .in_memory import InMemory
from .on_disk import OnDisk

# Base Non-Entity Types
from .regex import RegexValidator

# Usable Types
from .ascii import ASCII
from .date import Date, DateValidator, Datetime, DatetimeValidator
from .emojis import Emoji, Fuzzmoji, Vibemoji
from .integer import Integer
from .language import Language, LanguageName, LanguageCode
from .person import Person
from .regex import Email, SSN, ZipCode


__all__ = (
    "ASCII",
    "Date",
    "Email",
    "Emoji",
    "Entity",
    "EntitySource",
    "Fuzzmoji",
    "FuzzValidator",
    "InMemory",
    "Integer",
    "Language",
    "LanguageCode",
    "LanguageName",
    "Match",
    "MatchResult",
    "NamedEntity",
    "OnDisk",
    "Person",
    "Record",
    "RegexValidator",
    "SSN",
    "Date",
    "DateValidator",
    "Datetime",
    "DatetimeValidator",
    "Vibemoji",
    "ZipCode",
    "const",
    "flags",
    "get_type_adapter",
    "lazy",
    "logger",
    "utils",
    "validate_json",
    "validate_python",
)
