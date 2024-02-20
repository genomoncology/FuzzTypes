from typing import Callable

from . import FuzzType


def FindStr(source: Callable):
    return FuzzType(lookup_function=source)
