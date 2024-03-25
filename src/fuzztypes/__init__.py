__version__ = "0.1.1"

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

# Schema
from .entity import Entity, NamedEntity, EntitySource
from .match import Match, MatchResult, Record

# Validation
from .validation import (
    FuzzValidator,
    resolve_entity,
    validate_python,
    validate_json,
    get_type_adapter,
)

# Named Entity Storage
from . import storage
from .in_memory import InMemoryValidator
from .on_disk import OnDiskValidator

# Base Non-Entity Types
from .regex import RegexValidator

# Usable Types
from .ascii import ASCII
from .date import Date, DateValidator, Datetime, DatetimeValidator
from .emojis import Emoji, Fuzzmoji, Vibemoji
from .integer import Integer
from .language import (
    Language,
    LanguageCode,
    LanguageName,
    LanguageNamedEntity,
    LanguageScope,
    LanguageType,
)
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
    "InMemoryValidator",
    "Integer",
    "Language",
    "LanguageCode",
    "LanguageName",
    "LanguageNamedEntity",
    "LanguageScope",
    "LanguageType",
    "Match",
    "MatchResult",
    "NamedEntity",
    "OnDiskValidator",
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
    "resolve_entity",
    "validate_json",
    "validate_python",
)
