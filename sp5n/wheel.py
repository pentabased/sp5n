"""
wheel module maps keyboard input events to bends

spin() takes the current key state and a new key event, returns the
updated key state and optionally a bend (emitted on falling edges)
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

type KeyState = frozenset[Key]

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

# maps chord keys to bend kind petals
chord_key_map: Final[dict[Key, Petal]] = {
    "enter": "k",  # cant
    "space": "7",  # loop
    "left-shift": "y",  # yank
    "right-shift": "c",  # swerve
}


class EventKind(Enum):
    """key event states used internally by _evaluate"""

    RELEASED = -1
    HELD = 0


class SpinError(RuntimeError):
    """raised when spin() encounters ambiguous or invalid inputs"""


def current_chord(state: KeyState) -> Petal:
    """return the chord petal for the currently held keys"""
    for chord_key, petal in chord_key_map.items():
        if chord_key in state:
            return petal
    return "8"  # bloom (no chord key held)


def spin(
    state: KeyState, key: Key, pressed: bool
) -> tuple[KeyState, Bend | None]:
    """
    update key state with a new key event and emit a bend on falling edges

    on press (rising edge): adds key to state, returns None
    on release (falling edge): removes key from state, evaluates for a bend

    raises SpinError if:
    - multiple chord keys are active simultaneously
    - multiple glyph keys are active simultaneously
    - the glyph is not valid for the active chord kind
    """
    if pressed:
        return (state | {key}, None)

    # falling edge: build inputs snapshot and evaluate
    new_state = state - {key}
    inputs: dict[Key, EventKind] = {k: EventKind.HELD for k in new_state}
    inputs[key] = EventKind.RELEASED
    bend = _evaluate(inputs)
    return (new_state, bend)


def _evaluate(inputs: dict[Key, EventKind]) -> Bend | None:
    """
    try to evaluate a set of key input states into a bend

    returns a Bend when exactly one key is released, None if nothing is ready

    raises SpinError if:
    - multiple chord keys are active simultaneously
    - multiple glyph keys are active simultaneously
    - the glyph is not valid for the active chord kind
    - an unrecognized key is present
    """
    chord: Petal | None = None
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
        return Bend("8", glyph)

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
