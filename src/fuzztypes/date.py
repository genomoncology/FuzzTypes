import datetime
from typing import Optional, Union, Type

from . import Entity, MatchList, abstract, const, lazy

date_or_datetime = Union[datetime.date, datetime.datetime]


def DateType(
    date_order: const.DateOrder = None,
    examples: Optional[list] = None,
    languages: Optional[list[str]] = None,
    notfound_mode: const.NotFoundMode = "raise",
    input_type: Type[date_or_datetime] = datetime.date,
    timezone: Optional[str] = None,
    validator_mode: const.ValidatorMode = "before",
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[date_or_datetime] = None,
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

    def parse(key: str) -> MatchList:
        match_list = MatchList()
        value = parser.get_date_data(key).date_obj
        if value is not None:
            if input_type is datetime.date:
                value = value.date()
            entity = Entity(value=value)
            match_list.set(key=key, entity=entity)
        return match_list

    return abstract.AbstractType(
        parse,
        examples=examples,
        input_type=input_type,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


def DatetimeType(
    date_order: const.DateOrder = None,
    examples: Optional[list] = None,
    languages: Optional[list[str]] = None,
    notfound_mode: const.NotFoundMode = "raise",
    input_type: Type[date_or_datetime] = datetime.datetime,
    timezone: Optional[str] = None,
    validator_mode: const.ValidatorMode = "before",
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[date_or_datetime] = None,
):
    return DateType(
        date_order,
        examples,
        languages,
        notfound_mode,
        input_type,
        timezone,
        validator_mode,
        strict,
        prefer_future_dates,
        relative_base,
    )


Date = DateType()
Datetime = DatetimeType()
