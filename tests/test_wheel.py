"""
unit tests for sp5n.wheel
"""

import pytest

from sp5n.bend import Bend
from sp5n.wheel import SpinError, current_chord, spin


# --- spin: press events (rising edge) ---


def test_spin_press_adds_key():
    state, bend = spin(frozenset(), "qQ", pressed=True)
    assert state == frozenset({"qQ"})
    assert bend is None


def test_spin_press_accumulates():
    state, _ = spin(frozenset(), "space", pressed=True)
    state, bend = spin(state, "pP", pressed=True)
    assert state == frozenset({"space", "pP"})
    assert bend is None


# --- spin: release events (falling edge) ---


def test_spin_bloom():
    # press then release a glyph key with no chord
    state, _ = spin(frozenset(), "qQ", pressed=True)
    state, bend = spin(state, "qQ", pressed=False)
    assert bend == Bend("8", "Q")
    assert state == frozenset()


def test_spin_chord_and_glyph_release():
    # press chord + glyph, release both
    state = frozenset({"enter", "[{"})
    state, bend = spin(state, "enter", pressed=False)
    # enter released first — chord released with glyph still held
    # actually [{ is still held, so this produces a bend
    assert bend == Bend("k", "-")


def test_spin_chord_release_no_glyph():
    state = frozenset({"enter"})
    state, bend = spin(state, "enter", pressed=False)
    assert bend == Bend("k", "-")


def test_spin_multiple_chords():
    state = frozenset({"enter", "right-shift"})
    with pytest.raises(SpinError, match="chord keys"):
        spin(state, "enter", pressed=False)


def test_spin_multiple_glyphs():
    state = frozenset({"qQ", "wW"})
    with pytest.raises(SpinError, match="glyph keys"):
        spin(state, "qQ", pressed=False)


@pytest.mark.parametrize(
    "chord_key,kind_petal,glyph_key,glyph_petal",
    [
        ("enter", "k", "[{", "-"),
        ("right-shift", "c", "aA", "a"),
        ("left-shift", "y", "xX", "x"),
        ("space", "7", "[{", "-"),
    ],
)
def test_spin_valid_bends(chord_key, kind_petal, glyph_key, glyph_petal):
    state = frozenset({chord_key, glyph_key})
    _, bend = spin(state, glyph_key, pressed=False)
    assert bend == Bend(kind_petal, glyph_petal)


@pytest.mark.parametrize(
    "chord_key,glyph_key,expected_error",
    [
        ("enter", "hH", "no cant for 'h'"),
        ("right-shift", "jJ", "no swerve for 'j'"),
        ("left-shift", "qQ", "no yank for 'Q'"),
        ("space", "gG", "no loop for 'G'"),
    ],
)
def test_spin_invalid_bends(chord_key, glyph_key, expected_error):
    state = frozenset({chord_key, glyph_key})
    with pytest.raises(SpinError, match=expected_error):
        spin(state, glyph_key, pressed=False)


def test_uU_maps_to_ah():
    state = frozenset({"uU"})
    _, bend = spin(state, "uU", pressed=False)
    assert bend == Bend("8", "µ")


def test_all_glyph_keys_covered():
    from sp5n.wheel import glyph_key_map

    for key, petal in glyph_key_map.items():
        state = frozenset({key})
        _, bend = spin(state, key, pressed=False)
        assert bend == Bend("8", petal), f"failed for key '{key}'"


# --- current_chord ---


def test_current_chord_no_keys():
    assert current_chord(frozenset()) == "8"


def test_current_chord_bloom():
    assert current_chord(frozenset({"qQ"})) == "8"


def test_current_chord_loop():
    assert current_chord(frozenset({"space"})) == "7"


def test_current_chord_cant():
    assert current_chord(frozenset({"enter"})) == "k"


def test_current_chord_swerve():
    assert current_chord(frozenset({"right-shift"})) == "c"


def test_current_chord_yank():
    assert current_chord(frozenset({"left-shift"})) == "y"
