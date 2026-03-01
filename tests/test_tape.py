"""
unit tests for sp5n.tape
"""

from sp5n.bend import Bend
from sp5n.petal import Petal
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
    p = Panel(width=10, height=2, lines=("hello", "world"), shuttle=())
    assert p.width == 10
    assert p.lines == ("hello", "world")
    assert p.shuttle == ()


# --- pocket loom: bloom ---


def test_bloom_adds_petal():
    lm = loom()
    panel = lm.push(Bend("8", "h"))
    assert panel.lines[0] == "h"


def test_bloom_builds_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    panel = lm.push(Bend("8", "7"))
    assert panel.lines[0] == "h57"


# --- pocket loom: loop ---


def test_loop_neem_starts_new_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("7", "-"))
    panel = lm.push(Bend("8", "w"))
    assert panel.lines[0] == "h5 w"


def test_loop_phrase_starts_new_phrase():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))
    panel = lm.push(Bend("8", "w"))
    assert panel.lines[0] == "h"
    assert panel.lines[1] == "w"


# --- pocket loom: cant ---


def test_cant_suggest_is_no_op():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    panel = lm.push(Bend("k", "-"))
    # suggest is reserved — no change to content
    assert panel.lines[0] == "h5"


# --- pocket loom: swerve ---


def test_swerve_back_moves_to_previous_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    lm.push(Bend("c", "a"))
    # now typing should go into the first neem
    panel = lm.push(Bend("8", "5"))
    assert panel.lines[0] == "h5 w"


def test_swerve_forward_moves_to_next_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("c", "a"))
    lm.push(Bend("c", "6"))
    # should be back on second neem
    panel = lm.push(Bend("8", "w"))
    assert panel.lines[0] == "h w"


def test_swerve_back_at_start_is_safe():
    lm = loom()
    panel = lm.push(Bend("c", "a"))
    assert panel.lines[0] == ""


def test_swerve_forward_at_end_is_safe():
    lm = loom()
    panel = lm.push(Bend("c", "6"))
    assert panel.lines[0] == ""


# --- pocket loom: yank ---


def test_yank_delete_removes_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    lm.push(Bend("c", "a"))  # swerve back to first neem
    panel = lm.push(Bend("y", "-"))  # yank-delete
    assert panel.lines[0] == "w"


def test_yank_delete_last_neem_removes_phrase():
    lm = loom()
    # two phrases: "h" and "w"
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))
    lm.push(Bend("8", "w"))
    # delete "w" (the only neem in second phrase)
    panel = lm.push(Bend("y", "-"))
    assert panel.lines[0] == "h"
    assert panel.lines[1] == ""  # second phrase gone


def test_yank_delete_only_content():
    lm = loom()
    lm.push(Bend("8", "h"))
    panel = lm.push(Bend("y", "-"))
    # verse is empty but structurally intact
    assert panel.lines[0] == ""


def test_yank_delete_moves_shuttle_back():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    # delete second neem (current position)
    lm.push(Bend("y", "-"))
    # bloom should go into first neem (shuttle moved back)
    panel = lm.push(Bend("8", "5"))
    assert panel.lines[0] == "h5"


def test_yank_delete_on_empty_is_safe():
    lm = loom()
    panel = lm.push(Bend("y", "-"))
    assert panel.lines[0] == ""


# --- pocket loom: shuttle position ---


def test_shuttle_on_empty_neem():
    lm = loom()
    panel = lm.render()
    # empty neem: zero-width at (0, 0)
    assert panel.shuttle == ((0, 0, 0),)


def test_shuttle_on_typed_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    panel = lm.push(Bend("8", "5"))
    assert panel.shuttle == ((0, 0, 2),)


def test_shuttle_after_loop_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    panel = lm.push(Bend("7", "-"))
    # new empty neem after "h5 " at col 3
    assert panel.shuttle == ((0, 3, 3),)


def test_shuttle_after_swerve_back():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    panel = lm.push(Bend("c", "a"))
    # shuttle back to first neem "h"
    assert panel.shuttle == ((0, 0, 1),)


def test_shuttle_on_second_phrase():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))
    panel = lm.push(Bend("8", "w"))
    # second phrase on line 1
    assert panel.shuttle == ((1, 0, 1),)


def test_shuttle_wrapping():
    lm = PocketLoom(panel_width=5, panel_height=10)
    # he770-w476 wraps across line boundary
    petals: list[Petal] = ["h", "e", "7", "7", "0", "-", "w", "4", "7", "6"]
    for glyph in petals:
        lm.push(Bend("8", glyph))
    panel = lm.render()
    # neem spans two lines: "he770" on line 0, "-w476" on line 1
    assert panel.shuttle == ((0, 0, 5), (1, 0, 5))


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
    # he770-w476 ("hello-world" as a compound neem)
    petals: list[Petal] = ["h", "e", "7", "7", "0", "-", "w", "4", "7", "6"]
    for glyph in petals:
        lm.push(Bend("8", glyph))
    panel = lm.render()
    assert panel.lines[0] == "he770"
    assert panel.lines[1] == "-w476"
