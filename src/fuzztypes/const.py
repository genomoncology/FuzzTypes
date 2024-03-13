import os
from typing import Literal

# Home directory of fuzztypes library.
FuzzHome = "~/.local/fuzztypes/"
FuzzHome = os.path.expanduser(os.environ.get("FUZZTYPES_HOME", FuzzHome))
OnDiskPath = os.path.join(FuzzHome, "on_disk")

# Default encoder to use when generating semantic embeddings.
# Override with environment variable `FUZZTYPES_DEFAULT_ENCODER`.
DefaultEncoder = "sentence-transformers/paraphrase-MiniLM-L6-v2"
DefaultEncoder = os.environ.get("FUZZTYPES_DEFAULT_ENCODER", DefaultEncoder)

# Default path for storing models for sentence transformers.
ModelsPath = os.path.join(FuzzHome, "models")


# Date Ordering used when parsing ambiguous dates.
# https://dateparser.readthedocs.io/en/latest/settings.html#date-order
DateOrder = Literal["DMY", "MDY", "YMD"]

# Device to use for generating semantic embeddings and lancedb indexing.
# https://www.sbert.net/examples/applications/computing-embeddings/README.html
# https://lancedb.github.io/lance/read_and_write.html#indexing
DeviceList = Literal["cpu", "cuda", "mps"]

# Which rapidfuzz scorer to use?
# https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html
# Scorers:
# ratio: Calculates Levenshtein Distance similarity ratio
# partial_ratio: Compares substrings, good for different length strings
# token_set_ratio: Compares unique words, allows different word order
# partial_token_set_ratio: Like token_set_ratio but compares substrings
# token_sort_ratio: Sorts words before compare, good when order is irrelevant
# partial_token_sort_ratio: Like token_sort_ratio but compares substrings
# token_ratio: Averages token_sort_ratio and token_set_ratio
# partial_token_ratio: Averages partial token sort and set ratios
# WRatio: Weighted combination of different ratios based on string lengths
# QRatio: Faster version of ratio, less accurate
FuzzScorer = Literal[
    "ratio",
    "partial_ratio",
    "token_set_ratio",
    "partial_token_set_ratio",
    "token_sort_ratio",
    "partial_token_sort_ratio",
    "token_ratio",
    "partial_token_ratio",
    "WRatio",
    "QRatio",
]

# What happens if a matching entity is not found for key?
# raise: raises an exception if no matching entity found
# none: sets value to None if no matching entity found
# allow: passes through key
NotFoundMode = Literal["raise", "none", "allow"]


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
