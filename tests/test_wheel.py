"""
unit tests for sp5n.wheel
"""

import pytest

from sp5n.bend import Bend, BendKind
from sp5n.wheel import EventKind, SpinError, spin


def test_spin_no_input():
    assert spin({}) is None


def test_spin_unreleased_press():
    assert spin({"qQ": EventKind.PRESSED}) is None


def test_spin_bloom():
    assert spin({"qQ": EventKind.RELEASED}) == Bend(BendKind.BLOOM, "Q")


def test_spin_chord_and_glyph_release():
    assert spin(
        {"enter": EventKind.RELEASED, "[{": EventKind.RELEASED}
    ) == Bend(BendKind.CANT, "-")


def test_spin_chord_release_no_glyph():
    assert spin({"enter": EventKind.RELEASED}) == Bend(BendKind.CANT, "-")


def test_spin_multiple_chords():
    with pytest.raises(SpinError, match="chord keys 'k' and 'c' both active"):
        spin({"enter": EventKind.PRESSED, "right-shift": EventKind.HELD})


def test_spin_multiple_glyphs():
    with pytest.raises(SpinError, match="glyph keys 'Q' and 'w' both active"):
        spin({"qQ": EventKind.PRESSED, "wW": EventKind.HELD})


def test_spin_unexpected_key():
    with pytest.raises(SpinError, match="unexpected key 'unexpected'"):
        spin({"unexpected": EventKind.PRESSED})  # type: ignore


@pytest.mark.parametrize(
    "chord_key,bend_kind,glyph_key,petal",
    [
        ("enter", BendKind.CANT, "[{", "-"),
        ("right-shift", BendKind.SWERVE, "aA", "a"),
        ("left-shift", BendKind.YANK, "xX", "x"),
        ("space", BendKind.LOOP, "[{", "-"),
    ],
)
def test_spin_valid_bends(chord_key, bend_kind, glyph_key, petal):
    inputs = {chord_key: EventKind.RELEASED, glyph_key: EventKind.RELEASED}
    assert spin(inputs) == Bend(bend_kind, petal)


@pytest.mark.parametrize(
    "chord_key,glyph_key,expected_error",
    [
        ("enter", "qQ", "no cant for 'Q'"),
        ("right-shift", "jJ", "no swerve for 'j'"),
        ("left-shift", "qQ", "no yank for 'Q'"),
        ("space", "gG", "no loop for 'G'"),
    ],
)
def test_spin_invalid_bends(chord_key, glyph_key, expected_error):
    inputs = {chord_key: EventKind.RELEASED, glyph_key: EventKind.RELEASED}
    with pytest.raises(SpinError, match=expected_error):
        spin(inputs)


def test_uU_maps_to_ah():
    # uU should map to µ (AH), not ? (NG) - v0 had a duplicate mapping bug
    assert spin({"uU": EventKind.RELEASED}) == Bend(BendKind.BLOOM, "µ")


def test_all_glyph_keys_covered():
    # every glyph key should produce a bloom bend when released
    from sp5n.wheel import glyph_key_map

    for key, petal in glyph_key_map.items():
        result = spin({key: EventKind.RELEASED})
        assert result == Bend(BendKind.BLOOM, petal), f"failed for key '{key}'"
