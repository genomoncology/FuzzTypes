from datetime import datetime, date
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from fuzztypes import Date, DateType, DatetimeType, utils

ny_tz = ZoneInfo("America/New_York")

DateY2K = Annotated[
    datetime, DatetimeType(relative_base=datetime(2000, 1, 1), timezone="EST")
]


class MyModel(BaseModel):
    date: Date
    time: DateY2K


def test_validate_python_date_and_datetime():
    data = dict(date="11 July 2012", time="tomorrow 5am")
    obj = utils.validate_python(MyModel, data)
    assert obj.date == date(2012, 7, 11)
    assert obj.time == datetime(2000, 1, 2, 5, 0, 0, tzinfo=ny_tz)


def test_validate_json_date_and_datetime():
    json = '{"date": "July 4th", "time": "1 year ago"}'
    obj = utils.validate_json(MyModel, json)
    today = date.today()
    year = today.year if (today.month, today.day) >= (7, 4) else today.year - 1
    assert obj.date == date(year, 7, 4)
    assert obj.time == datetime(1999, 1, 1, 0, 0, 0, tzinfo=ny_tz)

    d = obj.date.isoformat()
    t = obj.time.isoformat()
    assert obj.model_dump_json() == f'{{"date":"{d}","time":"{t}"}}'


def test_mdy_vs_ymd():
    # MDY vs. YMD ordering is context specific
    # https://dateparser.readthedocs.io/en/latest/settings.html#date-order
    #
    assert utils.validate_python(Date, "02-03-04") == date(
        year=2004, month=2, day=3
    )

    DateEN = DateType(languages=["en"])
    assert utils.validate_python(DateEN, "02-03-04") == date(
        year=2004, month=2, day=3
    )

    DateMDY = DateType(date_order="MDY")
    assert utils.validate_python(DateMDY, "02-03-04") == date(
        year=2004, month=2, day=3
    )

    DateES = DateType(languages=["es"])
    assert utils.validate_python(DateES, "02-03-04") == date(
        year=2004, month=3, day=2
    )

    DateDMY = DateType(date_order="DMY")
    assert utils.validate_python(DateDMY, "02-03-04") == date(
        year=2004, month=3, day=2
    )

    DateYMD = DateType(date_order="YMD")
    assert utils.validate_python(DateYMD, "02-03-04") == date(
        year=2002, month=3, day=4
    )
