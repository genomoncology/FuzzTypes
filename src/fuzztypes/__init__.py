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

# Schema
from .entity import Entity, NamedEntity, EntitySource
from .match import Match, MatchResult, Record

# Hidden Abstract Types
from . import abstract

# Base Named Entity Types
from .in_memory import InMemory
from .on_disk import OnDisk

# Base Non-Entity Types
from .function import Function
from .regex import Regex

# Usable Types
from .ascii import ASCII
from .date import Date, DateType, Datetime, DatetimeType
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
    "Function",
    "Fuzzmoji",
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
    "Regex",
    "SSN",
    "Date",
    "DateType",
    "Datetime",
    "DatetimeType",
    "Vibemoji",
    "ZipCode",
    "const",
    "flags",
    "lazy",
    "logger",
    "utils",
)
