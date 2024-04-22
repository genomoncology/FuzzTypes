from typing import Literal


# Date Ordering used when parsing ambiguous dates.
# https://dateparser.readthedocs.io/en/latest/settings.html#date-order
DateOrder = Literal["DMY", "MDY", "YMD"]
