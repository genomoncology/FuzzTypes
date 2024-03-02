import datetime
from typing import Optional, Union, Type

from dateparser.date import DateDataParser

from . import AbstractType, Entity, MatchList, const

DateOrDateTime = Union[datetime.date, datetime.datetime]


def FuzzDate(
    date_order: const.DateOrder = None,
    examples: Optional[list] = None,
    languages: Optional[list[str]] = None,
    notfound_mode: const.NotFoundMode = "raise",
    python_type: Type[DateOrDateTime] = datetime.date,
    timezone: Optional[str] = None,
    validator_mode: const.ValidatorMode = "before",
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[DateOrDateTime] = None,
):
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
            if python_type is datetime.date:
                value = value.date()
            entity = Entity(value=value)
            match_list.set(key=key, entity=entity)
        return match_list

    return AbstractType(
        parse,
        examples=examples,
        notfound_mode=notfound_mode,
        python_type=python_type,
        validator_mode=validator_mode,
    )


def FuzzTime(
    date_order: const.DateOrder = None,
    examples: Optional[list] = None,
    languages: Optional[list[str]] = None,
    notfound_mode: const.NotFoundMode = "raise",
    python_type: Type[DateOrDateTime] = datetime.datetime,
    timezone: Optional[str] = None,
    validator_mode: const.ValidatorMode = "before",
    strict: bool = False,
    prefer_future_dates: bool = False,
    relative_base: Optional[DateOrDateTime] = None,
):
    return FuzzDate(
        date_order,
        examples,
        languages,
        notfound_mode,
        python_type,
        timezone,
        validator_mode,
        strict,
        prefer_future_dates,
        relative_base,
    )
