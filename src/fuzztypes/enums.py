from enum import Enum, EnumMeta
import sys
from typing import (
    Any,
    Callable,
    Optional,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

import rapidfuzz.fuzz
import rapidfuzz.process
from vokab import const

from . import FuzzValidator

if sys.version_info < (3, 11):

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return str(self.value)

else:
    from enum import StrEnum

E = TypeVar("E", bound=Union[StrEnum, Any])
IfMissing = Literal["pass_through", "raise_exception", "return_none"]


def EnumValidator(
    enum_or_literal: Type[E],
    min_similarity: float = 70.0,
    scorer: Union[Callable, const.FuzzScorerType] = "QRatio",
    if_missing: IfMissing = "return_none",
) -> Any:

    try:
        if callable(scorer):
            fuzz_scorer = scorer
        else:
            fuzz_scorer = getattr(rapidfuzz.fuzz, scorer)
    except AttributeError:
        fuzz_scorer = rapidfuzz.fuzz.QRatio

    mapping: dict[str, Any] = {}
    choices: List[str] = []
    members: List[Any] = []

    is_literal = get_origin(enum_or_literal) is Literal
    is_enum = type(enum_or_literal) is EnumMeta

    if is_literal:
        values = get_args(enum_or_literal)
        for value in values:
            key = str(value).lower()
            mapping[key] = value
            choices.append(key)
            members.append(value)

    elif is_enum:
        for member in enum_or_literal.__members__.values():
            key = str(member.name).lower()
            mapping[key] = member
            choices.append(key)
            members.append(member)

            key = str(member.value).lower()
            if key not in mapping:
                mapping[key] = member
                choices.append(key)
                members.append(member)
    else:
        raise ValueError(f"Invalid data type: {enum_or_literal}")

    def do_lookup(q: Optional[str]) -> Optional[str]:
        val: Optional[Any] = mapping.get(q.lower()) if q is not None else None

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

        if val is None:
            if if_missing == "raise_exception":
                raise ValueError(f"No match for {q} in {enum_or_literal}")

            elif if_missing == "pass_through":
                val = q

        elif is_enum:
            val = val.value

        return val

    return FuzzValidator(do_lookup)
