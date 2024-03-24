import datetime
from typing import Annotated, Optional, Union

from . import FuzzValidator, const, lazy

DateOrDatetime = Union[datetime.date, datetime.datetime]


def DateValidator(
    date_order: Optional[const.DateOrder] = None,
    is_date: bool = True,
    languages: Optional[list[str]] = None,
    timezone: Optional[str] = None,
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[DateOrDatetime] = None,
):
    DateDataParser = lazy.lazy_import("dateparser.date", "DateDataParser")
    languages = languages or ["en"]

    settings = {
        "STRICT_PARSING": strict,
        "PREFER_DATES_FROM": "future" if prefer_future_dates else "past",
        "RETURN_AS_TIMEZONE_AWARE": bool(timezone),
    }
    if date_order:
        settings["DATE_ORDER"] = date_order
    if timezone:
        settings["TIMEZONE"] = timezone
    if relative_base:
        settings["RELATIVE_BASE"] = relative_base

    parser = DateDataParser(languages=languages, settings=settings)

    def parse(key: str) -> DateOrDatetime:
        value = parser.get_date_data(key).date_obj
        value = value.date() if (value and is_date) else value
        return value

    return FuzzValidator(parse)


def DatetimeValidator(
    date_order: Optional[const.DateOrder] = None,
    languages: Optional[list[str]] = None,
    timezone: Optional[str] = None,
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[DateOrDatetime] = None,
):
    return DateValidator(
        date_order=date_order,
        is_date=False,
        languages=languages,
        timezone=timezone,
        strict=strict,
        prefer_future_dates=prefer_future_dates,
        relative_base=relative_base,
    )


Date = Annotated[datetime.date, DateValidator()]
Datetime = Annotated[datetime.datetime, DatetimeValidator()]
