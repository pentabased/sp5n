"""
unit tests for sp5n.tape
"""

from sp5n.bend import Bend, BendKind, CantKind, LoopKind, SwerveKind
from sp5n.tape import Panel, PocketLoom, render_neem, render_phrase


def loom() -> PocketLoom:
    return PocketLoom(panel_width=40, panel_height=10)


# --- render helpers ---


def test_render_neem():
    assert render_neem(["h", "5"]) == "h5"


def test_render_neem_empty():
    assert render_neem([]) == ""


def test_render_phrase():
    assert render_phrase([["h", "5"], ["2", "4"]]) == "h5 24"


def test_render_phrase_skips_empty_neems():
    assert render_phrase([["h", "5"], [], ["2"]]) == "h5 2"


# --- panel ---


def test_panel_is_frozen():
    p = Panel(width=10, height=2, lines=("hello", "world"))
    assert p.width == 10
    assert p.lines == ("hello", "world")


# --- pocket loom: bloom ---


def test_bloom_adds_petal():
    lm = loom()
    panel = lm.push(Bend(BendKind.BLOOM, "h"))
    assert panel.lines[0] == "h"


def test_bloom_builds_neem():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.BLOOM, "5"))
    panel = lm.push(Bend(BendKind.BLOOM, "7"))
    assert panel.lines[0] == "h57"


# --- pocket loom: loop ---


def test_loop_neem_starts_new_neem():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.BLOOM, "5"))
    lm.push(Bend(BendKind.LOOP, LoopKind.NEEM))
    panel = lm.push(Bend(BendKind.BLOOM, "w"))
    assert panel.lines[0] == "h5 w"


def test_loop_phrase_starts_new_phrase():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.LOOP, LoopKind.PHRASE))
    panel = lm.push(Bend(BendKind.BLOOM, "w"))
    assert panel.lines[0] == "h"
    assert panel.lines[1] == "w"


# --- pocket loom: cant / nope ---


def test_nope_removes_last_petal():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.BLOOM, "5"))
    panel = lm.push(Bend(BendKind.CANT, CantKind.NOPE))
    assert panel.lines[0] == "h"


def test_nope_on_empty_neem_is_safe():
    lm = loom()
    panel = lm.push(Bend(BendKind.CANT, CantKind.NOPE))
    assert panel.lines[0] == ""


# --- pocket loom: swerve ---


def test_swerve_back_moves_to_previous_neem():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.LOOP, LoopKind.NEEM))
    lm.push(Bend(BendKind.BLOOM, "w"))
    lm.push(Bend(BendKind.SWERVE, SwerveKind.BACK))
    # now typing should go into the first neem
    panel = lm.push(Bend(BendKind.BLOOM, "5"))
    assert panel.lines[0] == "h5 w"


def test_swerve_forward_moves_to_next_neem():
    lm = loom()
    lm.push(Bend(BendKind.BLOOM, "h"))
    lm.push(Bend(BendKind.LOOP, LoopKind.NEEM))
    lm.push(Bend(BendKind.SWERVE, SwerveKind.BACK))
    lm.push(Bend(BendKind.SWERVE, SwerveKind.FORWARD))
    # should be back on second neem
    panel = lm.push(Bend(BendKind.BLOOM, "w"))
    assert panel.lines[0] == "h w"


def test_swerve_back_at_start_is_safe():
    lm = loom()
    panel = lm.push(Bend(BendKind.SWERVE, SwerveKind.BACK))
    assert panel.lines[0] == ""


def test_swerve_forward_at_end_is_safe():
    lm = loom()
    panel = lm.push(Bend(BendKind.SWERVE, SwerveKind.FORWARD))
    assert panel.lines[0] == ""


# --- pocket loom: panel sizing ---


def test_panel_has_correct_dimensions():
    lm = PocketLoom(panel_width=20, panel_height=5)
    panel = lm.render()
    assert panel.width == 20
    assert panel.height == 5
    assert len(panel.lines) == 5


def test_panel_pads_empty_lines():
    lm = PocketLoom(panel_width=20, panel_height=3)
    panel = lm.render()
    assert panel.lines == ("", "", "")


def test_long_line_wraps():
    lm = PocketLoom(panel_width=5, panel_height=10)
    for glyph in ["h", "e", "7", "7", "0", "w", "4", "7", "6"]:
        lm.push(Bend(BendKind.BLOOM, glyph))
    panel = lm.render()
    assert panel.lines[0] == "he770"
    assert panel.lines[1] == "w476"
