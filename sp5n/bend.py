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
    """cant actions"""

    NOPE = "-"  # undo last petal (null glyph - enter alone)
    THUMP = "2"  # no-op


cant_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in CantKind
)


class SwerveKind(StrEnum):
    """shuttle movement actions"""

    BACK = "a"  # move shuttle backward one node
    FORWARD = "6"  # move shuttle forward one node
    GROW = "w"  # increase shuttle scope to next larger node
    SHRINK = "$"  # reduce shuttle scope to next smaller node
    SCOOP = "Q"  # expand shuttle backward
    STRETCH = "e"  # expand shuttle forward


swerve_glyphs: Final[frozenset[Petal]] = frozenset(
    kind.value for kind in SwerveKind
)


class YankKind(StrEnum):
    """scratch stack actions"""

    DELETE = "#"
    CUT = "x"
    COPY = "c"
    PASTE = "v"
    BRACKET = "8"


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


@dataclass
class Bend:
    """a single input event: one mode + one petal glyph"""

    kind: BendKind
    glyph: Petal
