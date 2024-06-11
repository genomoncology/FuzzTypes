from enum import Enum
import sys
from typing import Any, Callable, Optional, List, Type, TypeVar, Union

import rapidfuzz.fuzz
import rapidfuzz.process

from . import FuzzValidator

if sys.version_info < (3, 11):

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return str(self.value)

else:
    from enum import StrEnum


E = TypeVar("E", bound=StrEnum)


def EnumValidator(
    enum_cls: Type[E],
    min_similarity: float = 80.0,
    scorer: Union[Callable, str] = "QRatio",
) -> Any:

    try:
        if callable(scorer):
            fuzz_scorer = scorer
        else:
            fuzz_scorer = getattr(rapidfuzz.fuzz, scorer)
    except AttributeError:
        fuzz_scorer = rapidfuzz.fuzz.QRatio

    mapping: dict[str, E] = {}
    choices: List[str] = []
    members: List[E] = []

    for member in enum_cls.__members__.values():
        key = str(member.name).lower()
        mapping[key] = member
        choices.append(key)
        members.append(member)

        key = str(member.value).lower()
        if key not in mapping:
            mapping[key] = member
            choices.append(key)
            members.append(member)

    def do_lookup(q: str) -> Any:
        nonlocal fuzz_scorer, min_similarity, mapping, choices, members
        val: Optional[E] = mapping.get(q.lower())

        if val is None:
            # noinspection PyTypeChecker
            result = rapidfuzz.process.extractOne(
                q,
                choices=choices,
                score_cutoff=min_similarity,
                scorer=fuzz_scorer,
            )

            if result:
                _, similarity, index = result
                if similarity >= min_similarity:
                    val = members[index]

        return val.value if val else None

    return FuzzValidator(do_lookup)
