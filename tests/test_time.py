"""
unit tests for sp5n.time
"""

import datetime

import pytest

from sp5n.time import Time


def test_round_trip_int():
    t = Time(0)
    assert t.as_seconds == 0
    assert Time(t.as_stamp).as_seconds == 0


def test_round_trip_positive():
    seconds = 1_000_000_000  # 2001-09-09
    t = Time(seconds)
    assert t.as_seconds == seconds
    assert Time(t.as_stamp).as_seconds == seconds


def test_round_trip_negative():
    seconds = -1_000_000_000  # ~1938
    t = Time(seconds)
    assert t.as_seconds == seconds
    assert Time(t.as_stamp).as_seconds == seconds


def test_round_trip_max():
    seconds = (2**38) - 1
    t = Time(seconds)
    assert t.as_seconds == seconds
    assert Time(t.as_stamp).as_seconds == seconds


def test_round_trip_min():
    seconds = -(2**38)
    t = Time(seconds)
    assert t.as_seconds == seconds
    assert Time(t.as_stamp).as_seconds == seconds


def test_from_datetime():
    dt = datetime.datetime(2001, 9, 9, 1, 46, 40, tzinfo=datetime.timezone.utc)
    t = Time(dt)
    assert t.as_seconds == 1_000_000_000


def test_as_datetime():
    t = Time(1_000_000_000)
    dt = t.as_datetime
    assert dt.year == 2001
    assert dt.month == 9
    assert dt.day == 9


def test_subtraction():
    t1 = Time(1_000_000_100)
    t2 = Time(1_000_000_000)
    assert t1 - t2 == 100


def test_invalid_int_too_large():
    with pytest.raises(ValueError, match="wont fit in a stamp"):
        Time(2**38)


def test_invalid_int_too_small():
    with pytest.raises(ValueError, match="wont fit in a stamp"):
        Time(-(2**38) - 1)


def test_invalid_stamp_high_bit():
    # first petal with high bit set should raise
    from sp5n.petal import petal_order

    bad_first = petal_order[0x10]  # value 16, high bit set
    stamp = (bad_first,) + ("-",) * 7
    with pytest.raises(
        ValueError, match="high bit of the first petal must be zero"
    ):
        Time(stamp)  # type: ignore[assignment]


def test_now():
    t = Time.now()
    assert t.as_seconds > 0
