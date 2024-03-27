__version__ = "0.1.1.post1"

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
from .validator import FuzzValidator

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


from .adapter import (
    find_matches,
    get_type_adapter,
    get_validator,
    get_storage,
    resolve_entity,
    validate_json,
    validate_python,
)

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
    "find_matches",
    "flags",
    "get_storage",
    "get_type_adapter",
    "get_validator",
    "lazy",
    "logger",
    "resolve_entity",
    "utils",
    "validate_json",
    "validate_python",
)
