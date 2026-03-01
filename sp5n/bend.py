"""
bends encode input events streamed from a wheel to a loom

each bend is a mode (bloom/loop/yank/swerve/cant) plus a petal glyph
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from sp5n.petal import Petal


class BendKind(StrEnum):
    """the five input modes, each bound to a chord key"""

    BLOOM = "8"  # no chord key - spin petals into the current neem
    LOOP = "7"  # space - spin new loops into the document
    YANK = "y"  # left-shift - push/pop nodes to/from the scratch stack
    SWERVE = "c"  # right-shift - move the shuttle
    CANT = "k"  # enter - give commands to the loom


class CantKind(StrEnum):
    """cant actions

    the null glyph (enter alone, "-") is reserved for accepting
    suggestions from the loom (e.g. autocomplete, predictions)
    """

    SUGGEST = "-"  # accept loom suggestion (null glyph - enter alone)
    THUMP = "2"  # no-op
    QUIT = "Q"  # exit the wheel


cant_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in CantKind
)


class SwerveKind(StrEnum):
    """shuttle movement actions across four axes"""

    # scope axis (W/S keys)
    GROW = "w"  # expand shuttle scope to parent node
    SHRINK = "$"  # reduce shuttle scope to last child

    # tree axis (A/D keys)
    BACK = "a"  # move shuttle to previous sibling
    FORWARD = "6"  # move shuttle to next sibling

    # time axis (Z/X/C keys)
    UNDO = "#"  # step backward in edit history
    REDO_LEFT = "x"  # step forward, left branch at a fork
    REDO_RIGHT = "c"  # step forward, right branch at a fork

    # selection axis (Q/E keys)
    SCOOP = "Q"  # expand selection one child to the left
    STRETCH = "e"  # expand selection one child to the right


swerve_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in SwerveKind
)


class YankKind(StrEnum):
    """yank actions

    phase 1 implements DELETE only. scratch buffer actions (cut, copy,
    paste) will use the nine rightmost keys in phase 2.
    """

    DELETE = "-"  # remove node at shuttle scope (null glyph - shift alone)


yank_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in YankKind
)


class LoopKind(StrEnum):
    """loop node types that can be spun into the document via a loop bend

    phase 1 implements NEEM and PHRASE only
    """

    NEEM = "-"  # leaf node: a sequence of petals evoking a single word
    PHRASE = "p"  # stem node: a sequence of neems evoking a thought
    VERSE = "v"  # branch node: a sequence of phrases developing a theme


loop_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in LoopKind
)


@dataclass(frozen=True)
class Bend:
    """a single input event encoded as two petal glyphs (10 bits)"""

    kind: Petal
    glyph: Petal
