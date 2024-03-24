import re
from typing import Annotated, Optional

from . import FuzzValidator


def RegexValidator(
    pattern: str,
    examples: Optional[list] = None,
):
    regex = re.compile(pattern)

    def do_regex(key: str) -> Optional[str]:
        matches = regex.findall(key)
        if len(matches) == 1:
            return matches[0]

    return FuzzValidator(do_regex, examples=examples)


Email = Annotated[
    str,
    RegexValidator(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        examples=["user@example.com"],
    ),
]

SSN = Annotated[
    str,
    RegexValidator(
        r"\b\d{3}-\d{2}-\d{4}\b",
        examples=["000-00-0000"],
    ),
]

ZipCode = Annotated[
    str,
    RegexValidator(
        r"\b\d{5}(?:-\d{4})?\b",
        examples=["12345", "12345-6789"],
    ),
]
