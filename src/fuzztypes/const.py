import os
from typing import Literal


# Default GOTYPES_HOME
FUZZTYPES_HOME = os.environ.get("FUZZTYPES_HOME") or "~/.local/fuzztypes"
FUZZTYPES_HOME = os.path.expanduser(FUZZTYPES_HOME)


# Path to Vokab collection
FUZZTYPES_VOCAB_COLLECTION = os.environ.get(
    "FUZZTYPES_VOCAB_COLLECTION"
) or os.path.join(FUZZTYPES_HOME, "vokab")


# Date Ordering used when parsing ambiguous dates.
# https://dateparser.readthedocs.io/en/latest/settings.html#date-order
DateOrder = Literal["DMY", "MDY", "YMD"]
