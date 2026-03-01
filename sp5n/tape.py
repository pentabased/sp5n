"""
tape document node types and PocketLoom

a tape is a pentabased document scheme for narrative text

node hierarchy for phase 1 (bottom up):
  Neem   - a sequence of petals evoking a single word
  Phrase - a sequence of neems evoking a thought
  Verse  - a sequence of phrases developing a theme

PocketLoom is a minimal in-process loom stub that accepts bends and
maintains a single in-progress verse, emitting a rendered Panel on
each change
"""

from dataclasses import dataclass, field

from sp5n.bend import Bend, BendKind, LoopKind
from sp5n.petal import Petal

# --- node types ---

# mutable during authoring - built incrementally as bends arrive
Neem = list[Petal]
Phrase = list[Neem]
Verse = list[Phrase]


def render_neem(neem: Neem) -> str:
    """render a neem as a string of utf-8 glyphs"""
    return "".join(neem)


def render_phrase(phrase: Phrase) -> str:
    """render a phrase as space-separated neems"""
    return " ".join(render_neem(n) for n in phrase if n)


# --- panel ---


@dataclass(frozen=True)
class Panel:
    """a fixed-size block of rendered text produced by the loom"""

    width: int
    height: int
    lines: tuple[str, ...]


# --- pocket loom ---


@dataclass
class PocketLoom:
    """
    a minimal in-process loom stub for phase 1

    maintains a single in-progress verse and renders it to a Panel
    on each change

    the shuttle is a (phrase_index, neem_index) cursor into the verse
    """

    panel_width: int
    panel_height: int
    verse: Verse = field(default_factory=lambda: [[[]]])  # one phrase, one neem

    # shuttle position: (phrase index, neem index within that phrase)
    _phrase_idx: int = field(default=0, init=False)
    _neem_idx: int = field(default=0, init=False)

    @property
    def _current_neem(self) -> Neem:
        return self.verse[self._phrase_idx][self._neem_idx]

    @property
    def _current_phrase(self) -> Phrase:
        return self.verse[self._phrase_idx]

    def push(self, bend: Bend) -> Panel:
        """accept a bend and return the updated panel"""
        match bend.kind:
            case BendKind.BLOOM:
                self._current_neem.append(bend.glyph)

            case BendKind.LOOP:
                match bend.glyph:
                    case LoopKind.NEEM:
                        # start a new neem after the current one
                        self._current_phrase.insert(self._neem_idx + 1, [])
                        self._neem_idx += 1
                    case LoopKind.PHRASE:
                        # start a new phrase after the current one
                        self.verse.insert(self._phrase_idx + 1, [[]])
                        self._phrase_idx += 1
                        self._neem_idx = 0
                    case _:
                        pass  # other loop kinds reserved for phase 2

            case BendKind.CANT:
                pass  # suggest reserved for future loom integration

            case BendKind.SWERVE:
                self._swerve(bend.glyph)

            case _:
                pass  # yank reserved for phase 2

        return self.render()

    def _swerve(self, glyph: Petal) -> None:
        """move the shuttle"""
        from sp5n.bend import SwerveKind

        match glyph:
            case SwerveKind.BACK:
                if self._neem_idx > 0:
                    self._neem_idx -= 1
                elif self._phrase_idx > 0:
                    self._phrase_idx -= 1
                    self._neem_idx = len(self._current_phrase) - 1
            case SwerveKind.FORWARD:
                phrase = self._current_phrase
                if self._neem_idx < len(phrase) - 1:
                    self._neem_idx += 1
                elif self._phrase_idx < len(self.verse) - 1:
                    self._phrase_idx += 1
                    self._neem_idx = 0
            case SwerveKind.GROW:
                # move shuttle scope up to phrase level: go to start of phrase
                self._neem_idx = 0
            case SwerveKind.SHRINK:
                # move shuttle scope down: go to end of current neem (already there)
                pass
            case _:
                pass  # SCOOP and STRETCH reserved for phase 2

    def render(self) -> Panel:
        """render the current verse to a panel"""
        lines: list[str] = []
        for phrase in self.verse:
            line = render_phrase(phrase)
            # wrap long lines to panel width
            while len(line) > self.panel_width:
                lines.append(line[: self.panel_width])
                line = line[self.panel_width :]
            lines.append(line)

        # pad or trim to panel height
        lines = lines[: self.panel_height]
        while len(lines) < self.panel_height:
            lines.append("")

        return Panel(
            width=self.panel_width,
            height=self.panel_height,
            lines=tuple(lines),
        )
