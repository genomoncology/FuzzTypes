from datetime import datetime, date
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from fuzztypes import FuzzDate, FuzzTime

Y2K = datetime(2000, 1, 1, 0, 0, 0)

ny_tz = ZoneInfo("America/New_York")


class MyModel(BaseModel):
    date: FuzzDate()
    time: FuzzTime(relative_base=Y2K, timezone="EST")


def test_examples():
    obj = MyModel(date="11 July 2012", time="tomorrow 5am")
    assert obj.date == date(2012, 7, 11)
    assert obj.time == datetime(2000, 1, 2, 5, 0, 0, tzinfo=ny_tz)

    obj = MyModel(date="July 4th", time="1 year ago")
    today = date.today()
    year = today.year if (today.month, today.day) >= (7, 4) else today.year - 1
    assert obj.date == date(year, 7, 4)
    assert obj.time == datetime(1999, 1, 1, 0, 0, 0, tzinfo=ny_tz)


def test_mdy_vs_ymd():
    # MDY vs. YMD ordering is context specific
    # https://dateparser.readthedocs.io/en/latest/settings.html#date-order
    #
    Date = FuzzDate()
    assert Date["02-03-04"].value == date(year=2004, month=2, day=3)

    DateEN = FuzzDate(languages=["en"])
    assert DateEN["02-03-04"].value == date(year=2004, month=2, day=3)

    DateMDY = FuzzDate(date_order="MDY")
    assert DateMDY["02-03-04"].value == date(year=2004, month=2, day=3)

    DateES = FuzzDate(languages=["es"])
    assert DateES["02-03-04"].value == date(year=2004, month=3, day=2)

    DateDMY = FuzzDate(date_order="DMY")
    assert DateDMY["02-03-04"].value == date(year=2004, month=3, day=2)

    DateYMD = FuzzDate(date_order="YMD")
    assert DateYMD["02-03-04"].value == date(year=2002, month=3, day=4)
