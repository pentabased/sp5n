"""
unit tests for sp5n.tape
"""

from sp5n.bend import Bend
from sp5n.petal import Petal
from sp5n.tape import (
    Panel,
    PocketLoom,
    ShuttleScope,
    render_neem,
    render_phrase,
)


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


def test_bloom_sets_petal_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    assert lm._scope == ShuttleScope.PETAL
    assert lm._petal_idx == 0


def test_bloom_at_petal_scope_inserts_right():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    assert lm._petal_idx == 1
    lm.push(Bend("8", "7"))
    assert lm._petal_idx == 2
    assert lm._current_neem == ["h", "5", "7"]


def test_bloom_at_neem_scope_on_empty_neem():
    lm = loom()
    # initial scope is neem, neem is empty
    lm.push(Bend("8", "h"))
    assert lm._scope == ShuttleScope.PETAL
    assert lm._petal_idx == 0
    assert lm._current_neem == ["h"]


def test_bloom_at_neem_scope_on_nonempty_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    # grow to neem scope
    lm.push(Bend("c", "w"))
    assert lm._scope == ShuttleScope.NEEM
    # bloom at neem scope inserts at beginning (drill down left)
    lm.push(Bend("8", "7"))
    assert lm._scope == ShuttleScope.PETAL
    assert lm._petal_idx == 0
    assert lm._current_neem == ["7", "h", "5"]


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


def test_loop_neem_sets_neem_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    assert lm._scope == ShuttleScope.PETAL
    lm.push(Bend("7", "-"))
    assert lm._scope == ShuttleScope.NEEM


def test_loop_phrase_sets_phrase_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))
    assert lm._scope == ShuttleScope.PHRASE


# --- pocket loom: cant ---


def test_cant_suggest_is_no_op():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    panel = lm.push(Bend("k", "-"))
    # suggest is reserved — no change to content
    assert panel.lines[0] == "h5"


# --- pocket loom: swerve ---


def test_swerve_back_at_neem_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))  # neem scope
    lm.push(Bend("8", "w"))  # petal scope
    lm.push(Bend("c", "w"))  # grow → neem scope
    lm.push(Bend("c", "a"))  # back → neem scope on "h"
    # bloom at neem scope inserts at beginning
    panel = lm.push(Bend("8", "5"))
    assert panel.lines[0] == "5h w"


def test_swerve_forward_at_neem_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))  # neem scope
    lm.push(Bend("c", "a"))  # back → neem scope on "h"
    lm.push(Bend("c", "6"))  # forward → neem scope on empty neem
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


# --- pocket loom: swerve grow/shrink ---


def test_grow_from_petal_to_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    assert lm._scope == ShuttleScope.PETAL
    lm.push(Bend("c", "w"))  # grow
    assert lm._scope == ShuttleScope.NEEM


def test_grow_from_neem_to_phrase():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("c", "w"))  # → neem
    lm.push(Bend("c", "w"))  # → phrase
    assert lm._scope == ShuttleScope.PHRASE


def test_grow_from_phrase_to_verse():
    lm = loom()
    lm.push(Bend("c", "w"))  # neem → phrase
    lm.push(Bend("c", "w"))  # phrase → verse
    assert lm._scope == ShuttleScope.VERSE


def test_grow_at_verse_is_noop():
    lm = loom()
    lm.push(Bend("c", "w"))  # → phrase
    lm.push(Bend("c", "w"))  # → verse
    lm.push(Bend("c", "w"))  # no-op
    assert lm._scope == ShuttleScope.VERSE


def test_shrink_from_neem_to_petal():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("c", "w"))  # grow → neem
    lm.push(Bend("c", "$"))  # shrink → petal (last petal)
    assert lm._scope == ShuttleScope.PETAL
    assert lm._petal_idx == 1  # last petal "5"


def test_shrink_from_phrase_to_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    lm.push(Bend("c", "w"))  # → neem
    lm.push(Bend("c", "w"))  # → phrase
    lm.push(Bend("c", "$"))  # shrink → neem (last neem)
    assert lm._scope == ShuttleScope.NEEM
    assert lm._neem_idx == 1  # last neem "w"


def test_shrink_on_empty_neem_is_noop():
    lm = loom()
    # initial: neem scope on empty neem
    lm.push(Bend("c", "$"))  # can't shrink into empty neem
    assert lm._scope == ShuttleScope.NEEM


# --- pocket loom: swerve back/forward at petal scope ---


def test_petal_back_moves_to_previous_petal():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("8", "7"))
    assert lm._petal_idx == 2
    lm.push(Bend("c", "a"))  # back at petal scope
    assert lm._petal_idx == 1


def test_petal_forward_moves_to_next_petal():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("8", "7"))
    lm.push(Bend("c", "a"))  # back → petal 1
    lm.push(Bend("c", "6"))  # forward → petal 2
    assert lm._petal_idx == 2


def test_petal_back_at_first_is_noop():
    lm = loom()
    lm.push(Bend("8", "h"))
    assert lm._petal_idx == 0
    lm.push(Bend("c", "a"))  # can't go before first petal
    assert lm._petal_idx == 0


def test_petal_forward_at_last_is_noop():
    lm = loom()
    lm.push(Bend("8", "h"))
    assert lm._petal_idx == 0
    lm.push(Bend("c", "6"))  # can't go past last petal
    assert lm._petal_idx == 0


# --- pocket loom: yank ---


def test_yank_delete_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))  # neem scope
    lm.push(Bend("8", "w"))  # petal scope
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.push(Bend("y", "-"))  # delete neem "w"
    assert panel.lines[0] == "h"


def test_yank_delete_last_neem_removes_phrase():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))  # phrase scope
    lm.push(Bend("8", "w"))  # petal scope
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.push(Bend("y", "-"))  # delete neem "w" (only neem)
    assert panel.lines[0] == "h"
    assert panel.lines[1] == ""  # second phrase gone


def test_yank_delete_only_content():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.push(Bend("y", "-"))
    assert panel.lines[0] == ""


def test_yank_delete_neem_moves_shuttle_back():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.push(Bend("y", "-"))  # delete "w", shuttle back to "h"
    assert panel.shuttle == ((0, 0, 1),)  # neem scope on "h"


def test_yank_delete_on_empty_is_safe():
    lm = loom()
    panel = lm.push(Bend("y", "-"))
    assert panel.lines[0] == ""


# --- pocket loom: yank at petal scope ---


def test_yank_delete_petal():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("8", "7"))
    panel = lm.push(Bend("y", "-"))  # delete petal "7"
    assert panel.lines[0] == "h5"
    assert lm._scope == ShuttleScope.PETAL
    assert lm._petal_idx == 1  # now on "5"


def test_yank_delete_last_petal_goes_to_neem_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    panel = lm.push(Bend("y", "-"))  # delete only petal
    assert panel.lines[0] == ""
    assert lm._scope == ShuttleScope.NEEM


# --- pocket loom: shuttle position ---


def test_shuttle_on_empty_neem():
    lm = loom()
    panel = lm.render()
    # neem scope, empty neem: zero-width at (0, 0)
    assert panel.shuttle == ((0, 0, 0),)


def test_shuttle_petal_scope_after_bloom():
    lm = loom()
    lm.push(Bend("8", "h"))
    panel = lm.push(Bend("8", "5"))
    # petal scope on "5" (second char, col 1)
    assert panel.shuttle == ((0, 1, 2),)


def test_shuttle_neem_scope_via_grow():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.render()
    # neem scope: highlights entire "h5"
    assert panel.shuttle == ((0, 0, 2),)


def test_shuttle_after_loop_neem():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("8", "5"))
    panel = lm.push(Bend("7", "-"))
    # neem scope on new empty neem after "h5 " at col 3
    assert panel.shuttle == ((0, 3, 3),)


def test_shuttle_after_swerve_back_neem_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))  # neem scope
    lm.push(Bend("8", "w"))  # petal scope
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.push(Bend("c", "a"))  # back → neem "h"
    assert panel.shuttle == ((0, 0, 1),)


def test_shuttle_on_second_phrase():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "p"))
    panel = lm.push(Bend("8", "w"))
    # petal scope on "w", second phrase on line 1
    assert panel.shuttle == ((1, 0, 1),)


def test_shuttle_petal_wrapping():
    lm = PocketLoom(panel_width=5, panel_height=10)
    petals: list[Petal] = ["h", "e", "7", "7", "0", "-", "w", "4", "7", "6"]
    for glyph in petals:
        lm.push(Bend("8", glyph))
    panel = lm.render()
    # petal scope on "6" (last petal), col = 9 → line 1, col 4
    assert panel.shuttle == ((1, 4, 5),)


def test_shuttle_neem_wrapping():
    lm = PocketLoom(panel_width=5, panel_height=10)
    petals: list[Petal] = ["h", "e", "7", "7", "0", "-", "w", "4", "7", "6"]
    for glyph in petals:
        lm.push(Bend("8", glyph))
    lm.push(Bend("c", "w"))  # grow → neem scope
    panel = lm.render()
    # neem scope: spans two lines
    assert panel.shuttle == ((0, 0, 5), (1, 0, 5))


def test_shuttle_phrase_scope():
    lm = loom()
    lm.push(Bend("8", "h"))
    lm.push(Bend("7", "-"))
    lm.push(Bend("8", "w"))
    lm.push(Bend("c", "w"))  # → neem
    lm.push(Bend("c", "w"))  # → phrase
    panel = lm.render()
    # phrase scope: highlights entire line "h w" (3 chars)
    assert panel.shuttle == ((0, 0, 3),)


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
