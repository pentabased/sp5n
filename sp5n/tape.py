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
    """a fixed-size block of rendered text produced by the loom

    shuttle is a tuple of (line, start_col, end_col) segments indicating
    the highlighted neem. usually one segment; two if a neem wraps.
    start_col == end_col means a zero-width cursor (empty neem).
    """

    width: int
    height: int
    lines: tuple[str, ...]
    shuttle: tuple[tuple[int, int, int], ...]


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

            case BendKind.YANK:
                self._yank(bend.glyph)

            case _:
                pass

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

    def _yank(self, glyph: Petal) -> None:
        """remove or manipulate content at the shuttle"""
        from sp5n.bend import YankKind

        match glyph:
            case YankKind.DELETE:
                self._delete_at_shuttle()
            case _:
                pass  # scratch buffer reserved for phase 2

    def _delete_at_shuttle(self) -> None:
        """remove the neem at the shuttle and adjust position"""
        phrase = self._current_phrase

        if len(self.verse) == 1 and len(phrase) == 1:
            # last neem in last phrase — clear it, don't remove
            phrase[0] = []
            return

        # remove the current neem
        del phrase[self._neem_idx]

        if not phrase:
            # phrase is now empty — remove it too
            del self.verse[self._phrase_idx]
            # shuttle moves to previous phrase's last neem
            if self._phrase_idx > 0:
                self._phrase_idx -= 1
            self._neem_idx = len(self._current_phrase) - 1
        elif self._neem_idx >= len(phrase):
            # was the last neem in phrase — step back
            self._neem_idx = len(phrase) - 1

    def _compute_shuttle(
        self, phrase_start_lines: list[int]
    ) -> tuple[tuple[int, int, int], ...]:
        """compute shuttle highlight segments in rendered output"""
        phrase = self._current_phrase
        neem = self._current_neem

        # find column of shuttle neem within rendered phrase
        col = 0
        for n_idx, n in enumerate(phrase):
            if n_idx == self._neem_idx:
                break
            if n:  # empty neems skipped in rendering
                col += len(render_neem(n)) + 1  # +1 for space

        neem_len = len(render_neem(neem))
        start = col
        end = col + neem_len

        # map through line wrapping
        base_line = phrase_start_lines[self._phrase_idx]
        start_line = base_line + start // self.panel_width
        start_col = start % self.panel_width
        if end > start:
            end_line = base_line + (end - 1) // self.panel_width
            end_col = (end - 1) % self.panel_width + 1
        else:
            end_line = start_line
            end_col = start_col

        if start_line == end_line:
            return ((start_line, start_col, end_col),)
        else:
            # neem wraps across line boundary — two segments
            return (
                (start_line, start_col, self.panel_width),
                (end_line, 0, end_col),
            )

    def render(self) -> Panel:
        """render the current verse to a panel"""
        lines: list[str] = []
        phrase_start_lines: list[int] = []

        for phrase in self.verse:
            phrase_start_lines.append(len(lines))
            line = render_phrase(phrase)
            # wrap long lines to panel width
            while len(line) > self.panel_width:
                lines.append(line[: self.panel_width])
                line = line[self.panel_width :]
            lines.append(line)

        shuttle = self._compute_shuttle(phrase_start_lines)

        # pad or trim to panel height
        lines = lines[: self.panel_height]
        while len(lines) < self.panel_height:
            lines.append("")

        return Panel(
            width=self.panel_width,
            height=self.panel_height,
            lines=tuple(lines),
            shuttle=shuttle,
        )
