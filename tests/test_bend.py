"""
unit tests for sp5n.bend
"""

from sp5n.bend import (
    Bend,
    BendKind,
    CantKind,
    LoopKind,
    SwerveKind,
    YankKind,
    cant_glyphs,
    loop_glyphs,
    swerve_glyphs,
    yank_glyphs,
)


def test_bend_kind_values():
    assert BendKind.BLOOM == "8"
    assert BendKind.LOOP == "7"
    assert BendKind.YANK == "y"
    assert BendKind.SWERVE == "c"
    assert BendKind.CANT == "k"


def test_glyph_sets_match_enums():
    assert cant_glyphs == frozenset(k.value for k in CantKind)
    assert swerve_glyphs == frozenset(k.value for k in SwerveKind)
    assert yank_glyphs == frozenset(k.value for k in YankKind)
    assert loop_glyphs == frozenset(k.value for k in LoopKind)


def test_suggest_is_null_glyph():
    # suggest must be bound to the null glyph so enter-alone triggers it
    assert CantKind.SUGGEST == "-"


def test_bend_construction():
    bend = Bend(kind="8", glyph="a")
    assert bend.kind == "8"
    assert bend.glyph == "a"


def test_loop_phase1_nodes():
    # these three must exist for phase 1
    assert LoopKind.NEEM == "-"
    assert LoopKind.PHRASE == "p"
    assert LoopKind.VERSE == "v"
