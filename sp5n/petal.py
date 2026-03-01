"""
defines utf-8 glyphs for the 32 petals of pentabased

pentabased features 32 (2**5) petal glyphs stored as 5-bit binary numbers
that map to a visually distinct subset of the utf-8 character set

also provides Bloom (a sequence of 1-32 petals) and Word (a 64-bit value
stored as exactly 13 petals) for encoding and decoding pentabased data
"""

from collections.abc import Iterator, Sequence
from typing import Final, Literal, Self

type Petal = Literal[
    "-",
    "*",
    "2",
    "3",
    "4",
    "?",
    "a",
    "8",
    "c",
    "6",
    "e",
    "f",
    "G",
    "h",
    "5",
    "j",
    "k",
    "7",
    "m",
    "N",
    "0",
    "p",
    "Q",
    "r",
    "$",
    "t",
    "µ",
    "v",
    "w",
    "x",
    "y",
    "#",
]

petal_order: Final[tuple[Petal, ...]] = (
    "-",  # 0x00 0b00000 [beat]
    "*",  # 0x01 0b00001 [belonging | addressing]
    "2",  # 0x02 0b00010 TH
    "3",  # 0x03 0b00011 DH
    "4",  # 0x04 0b00100 ER
    "?",  # 0x05 0b00101 NG
    "a",  # 0x06 0b00110 AE
    "8",  # 0x07 0b00111 B
    "c",  # 0x08 0b01000 S
    "6",  # 0x09 0b01001 D
    "e",  # 0x0a 0b01010 EH
    "f",  # 0x0b 0b01011 F
    "G",  # 0x0c 0b01100 G
    "h",  # 0x0d 0b01101 H
    "5",  # 0x0e 0b01110 IH
    "j",  # 0x0f 0b01111 JH
    "k",  # 0x10 0b10000 K
    "7",  # 0x11 0b10001 L
    "m",  # 0x12 0b10010 M
    "N",  # 0x13 0b10011 N
    "0",  # 0x14 0b10100 OW
    "p",  # 0x15 0b10101 P
    "Q",  # 0x16 0b10110 CH
    "r",  # 0x17 0b10111 R
    "$",  # 0x18 0b11000 ZH
    "t",  # 0x19 0b11001 T
    "µ",  # 0x1a 0b11010 AH
    "v",  # 0x1b 0b11011 V
    "w",  # 0x1c 0b11100 W
    "x",  # 0x1d 0b11101 SH
    "y",  # 0x1e 0b11110 Y
    "#",  # 0x1f 0b11111 Z
)

petal_value: Final[dict[Petal, int]] = {
    "-": 0x00,  # [beat]
    "*": 0x01,  # [belonging | addressing]
    "2": 0x02,  # TH
    "3": 0x03,  # DH
    "4": 0x04,  # ER
    "?": 0x05,  # NG
    "a": 0x06,  # AE
    "8": 0x07,  # B
    "c": 0x08,  # S
    "6": 0x09,  # D
    "e": 0x0A,  # EH
    "f": 0x0B,  # F
    "G": 0x0C,  # G
    "h": 0x0D,  # H
    "5": 0x0E,  # IH
    "j": 0x0F,  # JH
    "k": 0x10,  # K
    "7": 0x11,  # L
    "m": 0x12,  # M
    "N": 0x13,  # N
    "0": 0x14,  # OW
    "p": 0x15,  # P
    "Q": 0x16,  # CH
    "r": 0x17,  # R
    "$": 0x18,  # ZH
    "t": 0x19,  # T
    "µ": 0x1A,  # AH
    "v": 0x1B,  # V
    "w": 0x1C,  # W
    "x": 0x1D,  # SH
    "y": 0x1E,  # Y
    "#": 0x1F,  # Z
}


class Bloom:
    """a sequence of 1-32 petals with bidirectional int conversion"""

    def __init__(self, petals: Sequence[Petal]):
        self._petals: tuple[Petal, ...] = tuple(petals)

    def __len__(self) -> int:
        return len(self._petals)

    def __getitem__(self, index: int) -> Petal:
        return self._petals[index]

    def __iter__(self) -> Iterator[Petal]:
        return iter(self._petals)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__eq__(other._petals)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__ne__(other._petals)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__lt__(other._petals)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__gt__(other._petals)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__le__(other._petals)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Bloom):
            return NotImplemented
        return self._petals.__ge__(other._petals)

    def int_at(self, index: int) -> int:
        return petal_value[self._petals[index]]

    @property
    def as_int(self) -> int:
        """convert the petal sequence to an integer value"""
        value = 0
        for petal in self._petals:
            value = (value << 5) | petal_value[petal]
        return value

    @classmethod
    def from_int(cls, value: int, length: int | None = None) -> Self:
        """create a bloom from an integer value, optionally padded to length"""
        if length is None:
            length = int(value.bit_length() / 5) + 1

        petals = []
        for i in range(length - 1, -1, -1):
            order: int = (value >> (i * 5)) & 0x1F
            petals.append(petal_order[order])

        return cls(petals)


class Word:
    """
    a 64-bit value stored as exactly 13 petals

    the high bit of the first petal must be zero so the value fits in a
    signed 64-bit integer - valid range is -(2**63) to (2**63)-1
    """

    def __init__(self, value: Bloom | int):
        if isinstance(value, int):
            if not -(2**63) <= value < 2**63:
                raise ValueError(
                    f"int value '{value}' wont fit in a 64 bit signed integer"
                )
            self._value = value

        elif isinstance(value, Bloom):
            if len(value) > 13:
                raise ValueError(
                    "cant create word from a bloom with more than 13 petals"
                )
            if len(value) == 13 and value.int_at(0) & 0x10:
                raise ValueError(
                    "cant create word from a bloom with more than 64 bits"
                )
            self._value = value.as_int

        else:
            raise TypeError(f"cant create word from type '{type(value)}'")

    def __getitem__(self, key: int) -> Petal:
        return self.as_bloom[key]

    @property
    def as_int(self) -> int:
        return self._value

    @property
    def as_bloom(self) -> Bloom:
        # mask to 64 bits to handle negative values (python bigint adds a 65th bit)
        value: int = self._value & 0xFFFFFFFFFFFFFFFF
        return Bloom.from_int(value, 13)
