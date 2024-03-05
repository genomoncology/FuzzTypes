from typing import Literal
from enum import Flag, auto

# Date Ordering used when parsing ambiguous dates.
# https://dateparser.readthedocs.io/en/latest/settings.html#date-order
DateOrder = Literal["DMY", "MDY", "YMD"]

# Which rapidfuzz scorer to use?
# https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html
# Have only tested "token_sort_ratio" for my use cases.
# Others are likely viable, just need to be able to explain use cases clearly.
FuzzScorer = Literal["token_sort_ratio"]

# What happens if a matching entity is not found for key?
# raise: raises an exception if no matching entity found
# none: sets value to None if no matching entity found
# allow: passes through key
NotFoundMode = Literal["raise", "none", "allow"]


# What NamedEntity fields does the search key need to match on?
# Does search support fuzzy matching and semantic similarity?
class SearchMode(Flag):
    NAME_OK = auto()
    ALIAS_OK = auto()
    FUZZ_OK = auto()
    SEMANTIC_OK = auto()

    NAME = NAME_OK
    ALIAS = NAME_OK | ALIAS_OK
    FUZZ = NAME_OK | ALIAS_OK | FUZZ_OK
    SEMANTIC = NAME_OK | ALIAS_OK | SEMANTIC_OK

    DEFAULT = ALIAS
    HYBRID = FUZZ | SEMANTIC

    @property
    def is_name_ok(self):
        return self & SearchMode.NAME_OK

    @property
    def is_alias_ok(self):
        return self & SearchMode.ALIAS_OK

    @property
    def is_fuzz_ok(self):
        return self & SearchMode.FUZZ_OK

    @property
    def is_semantic_ok(self):
        return self & SearchMode.SEMANTIC_OK

    @property
    def is_fuzz_or_semantic_ok(self):
        return (self & SearchMode.FUZZ_OK) | (self & SearchMode.SEMANTIC_OK)


# What happens if there is a tie?
# raise: raise an exception if two elements are tied without Entity.priority
# lesser: use lower Entity.value, if Entity.priority not set or different
# greater: use greater Entity.value, if Entity.priority not set or different
TiebreakerMode = Literal["raise", "lesser", "greater"]

# Which Pydantic validator mode?
# https://docs.pydantic.dev/latest/concepts/validators/
# Only 'before' has been tested, 'plain' may work with no changes.
# Refactoring probably required for 'after' and 'wrap'.
ValidatorMode = Literal["before"]  # ... , "after", "plain", "wrap"]
