"""
wheel module maps keyboard input events to bends in a thread

spin() takes a snapshot of active key states and returns a Bend when a key
is released, or None if no bend is ready yet
"""

from enum import Enum
from typing import Final, Literal

from sp5n.bend import (
    Bend,
    BendKind,
    cant_glyphs,
    loop_glyphs,
    swerve_glyphs,
    yank_glyphs,
)
from sp5n.petal import Petal

type Key = Literal[
    "qQ",
    "wW",
    "eE",
    "rR",
    "tT",
    "yY",
    "uU",
    "iI",
    "oO",
    "pP",
    "[{",
    "aA",
    "sS",
    "dD",
    "fF",
    "gG",
    "hH",
    "jJ",
    "kK",
    "lL",
    ";:",
    "'\"",
    "zZ",
    "xX",
    "cC",
    "vV",
    "bB",
    "nN",
    "mM",
    ",<",
    ".>",
    "/?",
    "enter",
    "space",
    "left-shift",
    "right-shift",
]

# maps glyph keys to petals
# q-row: Q w e r t y µ 5 0 p -
# a-row: a $ 6 f G h j k 7 * 2
# z-row: # x c v 8 N m 3 4 ?
glyph_key_map: Final[dict[Key, Petal]] = {
    "qQ": "Q",  # CH
    "wW": "w",  # W
    "eE": "e",  # EH
    "rR": "r",  # R
    "tT": "t",  # T
    "yY": "y",  # Y
    "uU": "µ",  # AH
    "iI": "5",  # IH
    "oO": "0",  # OW
    "pP": "p",  # P
    "[{": "-",  # [beat] / null
    "aA": "a",  # AE
    "sS": "$",  # ZH
    "dD": "6",  # D
    "fF": "f",  # F
    "gG": "G",  # G
    "hH": "h",  # H
    "jJ": "j",  # JH
    "kK": "k",  # K
    "lL": "7",  # L
    ";:": "*",  # [belonging | addressing]
    "'\"": "2",  # TH
    "zZ": "#",  # Z
    "xX": "x",  # SH
    "cC": "c",  # S
    "vV": "v",  # V
    "bB": "8",  # B
    "nN": "N",  # N
    "mM": "m",  # M
    ",<": "3",  # DH
    ".>": "4",  # ER
    "/?": "?",  # NG
}

# maps chord keys to bend kinds
chord_key_map: Final[dict[Key, BendKind]] = {
    "enter": BendKind.CANT,
    "space": BendKind.LOOP,
    "left-shift": BendKind.YANK,
    "right-shift": BendKind.SWERVE,
}


class EventKind(Enum):
    """key event states"""

    RELEASED = -1
    HELD = 0
    PRESSED = 1


class SpinError(RuntimeError):
    """raised when spin() is called with ambiguous or invalid inputs"""


def spin(inputs: dict[Key, EventKind]) -> Bend | None:
    """
    try to spin a set of key input events into a bend

    returns a Bend when exactly one key is released, None if nothing is ready

    raises SpinError if:
    - multiple chord keys are active simultaneously
    - multiple glyph keys are active simultaneously
    - the glyph is not valid for the active chord kind
    - an unrecognized key is present
    """
    chord: BendKind | None = None
    chord_released: bool = False
    glyph: Petal | None = None
    glyph_released: bool = False

    for key, event in inputs.items():
        if key in chord_key_map:
            if chord is not None:
                raise SpinError(
                    f"chord keys '{chord}' and '{chord_key_map[key]}' both active"
                )
            chord = chord_key_map[key]
            if event == EventKind.RELEASED:
                chord_released = True

        elif key in glyph_key_map:
            if glyph is not None:
                raise SpinError(
                    f"glyph keys '{glyph}' and '{glyph_key_map[key]}' both active"
                )
            glyph = glyph_key_map[key]
            if event == EventKind.RELEASED:
                glyph_released = True

        else:
            raise SpinError(f"unexpected key '{key}'")

    # nothing released yet - no bend to emit
    if not chord_released and not glyph_released:
        return None

    # no chord - bloom bend or nothing
    if chord is None:
        if glyph is None:
            return None
        return Bend(BendKind.BLOOM, glyph)

    # chord with no glyph - use null glyph
    if glyph is None:
        glyph = "-"

    # validate glyph for the active chord kind
    match chord:
        case BendKind.CANT:
            if glyph not in cant_glyphs:
                raise SpinError(f"no cant for '{glyph}'")
        case BendKind.SWERVE:
            if glyph not in swerve_glyphs:
                raise SpinError(f"no swerve for '{glyph}'")
        case BendKind.YANK:
            if glyph not in yank_glyphs:
                raise SpinError(f"no yank for '{glyph}'")
        case BendKind.LOOP:
            if glyph not in loop_glyphs:
                raise SpinError(f"no loop for '{glyph}'")
        case _:
            raise SpinError(f"unexpected bend kind '{chord}'")

    return Bend(chord, glyph)
