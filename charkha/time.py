"""
provides a 39-bit signed integer time stamp represented as a tuple of 8 petals

signifies the number of seconds since the unix epoch (midnight 1 january 1970)
capable of representing dates from roughly 6700 bce to 10000 ce
"""

import datetime
import time
from typing import Self

from charkha.petal import Petal, petal_order, petal_value

type Stamp = tuple[Petal, Petal, Petal, Petal, Petal, Petal, Petal, Petal]


class Time:
    """
    a 39-bit signed integer time stamp: seconds since the unix epoch

    can be constructed from an int, a datetime, or an 8-petal Stamp
    valid range: -(2**38) to (2**38)-1  (~6700 bce to ~10000 ce)
    """

    def __init__(self, seconds_since_epoch: Stamp | int | datetime.datetime):
        if isinstance(seconds_since_epoch, int):
            if not -(2**38) <= seconds_since_epoch < 2**38:
                raise ValueError(
                    f"int value '{seconds_since_epoch}' wont fit in a stamp"
                )
            self._seconds = seconds_since_epoch

        elif isinstance(seconds_since_epoch, datetime.datetime):
            self._seconds = int(seconds_since_epoch.timestamp())

        elif isinstance(seconds_since_epoch, tuple):
            if petal_value[seconds_since_epoch[0]] & 0x10:
                raise ValueError("high bit of the first petal must be zero")
            value = 0
            for petal in seconds_since_epoch:
                value = (value << 5) | petal_value[petal]
            # sign-extend from 39-bit to python int
            if value & (1 << 38):
                value -= 1 << 39
            self._seconds = value

        else:
            raise TypeError(
                f"cant create time from type '{type(seconds_since_epoch)}'"
            )

    def __sub__(self, other: Self) -> int:
        """return the difference in seconds between two time stamps"""
        return self._seconds - other._seconds

    @property
    def as_stamp(self) -> Stamp:
        # mask to 39 bits to handle negative values (python bigint)
        seconds: int = self._seconds & 0x7FFFFFFFFF

        petals = []
        for i in range(7, -1, -1):
            order: int = (seconds >> (i * 5)) & 0x1F
            petals.append(petal_order[order])

        return tuple(petals)

    @property
    def as_seconds(self) -> int:
        return self._seconds

    @property
    def as_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            self._seconds, tz=datetime.timezone.utc
        )

    @classmethod
    def now(cls) -> Self:
        return cls(int(time.time()))
