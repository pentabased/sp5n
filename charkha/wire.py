"""
wire protocol — charkha client side

encodes bends as 2-byte datagrams for sending to tiraz
decodes petal glyph streams from tiraz into display structures
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from charkha.bend import Bend
from charkha.petal import (
    Bloom,
    Petal,
    Word,
    decode_int,
    petal_order,
    petal_value,
)


# --- shuttle scope (matches tiraz.plaza.ShuttleScope) ---


class ShuttleScope(StrEnum):
    PETAL = "petal"
    NEEM = "neem"
    PHRASE = "phrase"
    VERSE = "verse"


GLYPH_SCOPES: dict[Petal, ShuttleScope] = {
    "*": ShuttleScope.PETAL,
    "N": ShuttleScope.NEEM,
    "p": ShuttleScope.PHRASE,
    "v": ShuttleScope.VERSE,
}


# --- display data types ---


@dataclass(frozen=True)
class Highlight:
    segments: tuple[tuple[int, int, int], ...]
    scope: ShuttleScope


@dataclass(frozen=True)
class Frame:
    screed_id: Word
    warp_id: Word
    width: int
    lines: tuple[str, ...]
    highlight: Highlight | None


@dataclass(frozen=True)
class Panel:
    x: int
    y: int
    width: int
    height: int
    frames: tuple[Frame, ...]
    scroll_offset: int = 0


@dataclass(frozen=True)
class Display:
    width: int
    height: int
    panels: tuple[Panel, ...]
    skein_id: Word | None


# --- wire kind glyphs ---

DISPLAY_KIND: Petal = "6"
PANEL_KIND: Petal = "p"
FRAME_KIND: Petal = "f"
HIGHLIGHT_KIND: Petal = "h"
WORD_KIND: Petal = "w"
NULL: Petal = "-"


# --- bend encoding ---


def encode_bend(bend: Bend) -> bytes:
    """encode a bend as a 2-byte datagram"""
    return bytes([petal_value[bend.kind], petal_value[bend.glyph]])


# --- display decoding ---


class DisplayParser:
    """parse a petal glyph stream into display structures"""

    def __init__(self, glyphs: Sequence[Petal]) -> None:
        self._glyphs = glyphs
        self._pos = 0

    def _next(self) -> Petal:
        g = self._glyphs[self._pos]
        self._pos += 1
        return g

    def _expect(self, expected: Petal) -> None:
        g = self._next()
        if g != expected:
            raise ValueError(
                f"expected '{expected}' at position {self._pos - 1}, got '{g}'"
            )

    def _read_int(self) -> int:
        value, self._pos = decode_int(self._glyphs, self._pos)
        return value

    def _read_word(self) -> Word:
        petals = [self._next() for _ in range(13)]
        return Word(Bloom(petals))

    def _read_optional_word(self) -> Word | None:
        g = self._glyphs[self._pos]
        if g == NULL:
            self._pos += 1
            return None
        self._expect(WORD_KIND)
        return self._read_word()

    def _read_line(self) -> str:
        length = self._read_int()
        chars: list[str] = []
        for _ in range(length):
            p = self._next()
            if p == "-":
                chars.append(" ")
            else:
                chars.append(p)
        return "".join(chars)

    def parse_highlight(self) -> Highlight | None:
        g = self._glyphs[self._pos]
        if g == NULL:
            self._pos += 1
            return None
        self._expect(HIGHLIGHT_KIND)
        scope_glyph = self._next()
        scope = GLYPH_SCOPES[scope_glyph]
        seg_count = self._read_int()
        segments: list[tuple[int, int, int]] = []
        for _ in range(seg_count):
            line = self._read_int()
            start_col = self._read_int()
            end_col = self._read_int()
            segments.append((line, start_col, end_col))
        return Highlight(segments=tuple(segments), scope=scope)

    def parse_frame(self) -> Frame:
        self._expect(FRAME_KIND)
        screed_id = self._read_word()
        warp_id = self._read_word()
        width = self._read_int()
        line_count = self._read_int()
        lines = tuple(self._read_line() for _ in range(line_count))
        highlight = self.parse_highlight()
        return Frame(
            screed_id=screed_id,
            warp_id=warp_id,
            width=width,
            lines=lines,
            highlight=highlight,
        )

    def parse_panel(self) -> Panel:
        self._expect(PANEL_KIND)
        x = self._read_int()
        y = self._read_int()
        width = self._read_int()
        height = self._read_int()
        scroll_offset = self._read_int()
        frame_count = self._read_int()
        frames = tuple(self.parse_frame() for _ in range(frame_count))
        return Panel(
            x=x,
            y=y,
            width=width,
            height=height,
            frames=frames,
            scroll_offset=scroll_offset,
        )

    def parse_display(self) -> Display:
        self._expect(DISPLAY_KIND)
        width = self._read_int()
        height = self._read_int()
        skein_id = self._read_optional_word()
        panel_count = self._read_int()
        panels = tuple(self.parse_panel() for _ in range(panel_count))
        return Display(
            width=width,
            height=height,
            panels=panels,
            skein_id=skein_id,
        )


def decode_display(data: bytes) -> Display:
    """decode a petal byte stream into a Display"""
    glyphs = tuple(petal_order[b & 0x1F] for b in data)
    parser = DisplayParser(glyphs)
    return parser.parse_display()
