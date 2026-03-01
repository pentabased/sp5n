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
from enum import StrEnum

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


# --- shuttle scope ---


class ShuttleScope(StrEnum):
    """scope levels for the shuttle cursor within a verse"""

    PETAL = "petal"
    NEEM = "neem"
    PHRASE = "phrase"
    VERSE = "verse"


# --- panel ---


@dataclass(frozen=True)
class Panel:
    """a fixed-size block of rendered text produced by the loom

    shuttle is a tuple of (line, start_col, end_col) segments indicating
    the highlighted region. scope determines what is highlighted:
    petal = single character, neem = whole word, phrase = whole line,
    verse = all content. start_col == end_col means a zero-width cursor.
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

    the shuttle has a position (phrase_idx, neem_idx, petal_idx) and
    a scope (petal, neem, phrase, verse)
    """

    panel_width: int
    panel_height: int
    verse: Verse = field(default_factory=lambda: [[[]]])  # one phrase, one neem

    # shuttle position
    _phrase_idx: int = field(default=0, init=False)
    _neem_idx: int = field(default=0, init=False)
    _petal_idx: int = field(default=0, init=False)
    _scope: ShuttleScope = field(default=ShuttleScope.NEEM, init=False)

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
                self._bloom(bend.glyph)

            case BendKind.LOOP:
                self._loop(bend.glyph)

            case BendKind.CANT:
                pass  # suggest reserved for future loom integration

            case BendKind.SWERVE:
                self._swerve(bend.glyph)

            case BendKind.YANK:
                self._yank(bend.glyph)

            case _:
                pass

        return self.render()

    def _bloom(self, glyph: Petal) -> None:
        """insert a petal at the shuttle position

        at petal scope: insert to the right of current petal
        at higher scopes: drill down left, insert at beginning
        """
        match self._scope:
            case ShuttleScope.PETAL:
                neem = self._current_neem
                pos = self._petal_idx + 1
                neem.insert(pos, glyph)
                self._petal_idx = pos

            case ShuttleScope.NEEM:
                neem = self._current_neem
                if neem:
                    # non-empty: drill down left, insert at beginning
                    neem.insert(0, glyph)
                else:
                    neem.append(glyph)
                self._petal_idx = 0
                self._scope = ShuttleScope.PETAL

            case ShuttleScope.PHRASE:
                phrase = self._current_phrase
                if len(phrase) == 1 and not phrase[0]:
                    # single empty neem: use it
                    phrase[0].append(glyph)
                    self._neem_idx = 0
                else:
                    # scaffold new neem at beginning of phrase
                    phrase.insert(0, [glyph])
                    self._neem_idx = 0
                self._petal_idx = 0
                self._scope = ShuttleScope.PETAL

            case ShuttleScope.VERSE:
                # drill down to first phrase, then follow phrase logic
                self._phrase_idx = 0
                phrase = self._current_phrase
                if len(phrase) == 1 and not phrase[0]:
                    phrase[0].append(glyph)
                    self._neem_idx = 0
                else:
                    phrase.insert(0, [glyph])
                    self._neem_idx = 0
                self._petal_idx = 0
                self._scope = ShuttleScope.PETAL

    def _loop(self, glyph: Petal) -> None:
        """insert a new node (neem or phrase) based on scope"""
        match glyph:
            case LoopKind.NEEM:
                if self._scope in (ShuttleScope.PETAL, ShuttleScope.NEEM):
                    # neem >= current scope: insert RIGHT
                    self._current_phrase.insert(self._neem_idx + 1, [])
                    self._neem_idx += 1
                elif self._scope == ShuttleScope.PHRASE:
                    # neem < phrase: insert LEFT (beginning of phrase)
                    self._current_phrase.insert(0, [])
                    self._neem_idx = 0
                else:
                    # neem < verse: drill down left, insert at first phrase
                    self._phrase_idx = 0
                    self._current_phrase.insert(0, [])
                    self._neem_idx = 0
                self._scope = ShuttleScope.NEEM

            case LoopKind.PHRASE:
                if self._scope == ShuttleScope.VERSE:
                    # phrase < verse: insert LEFT (beginning of verse)
                    self.verse.insert(0, [[]])
                    self._phrase_idx = 0
                else:
                    # phrase >= current scope: insert RIGHT
                    self.verse.insert(self._phrase_idx + 1, [[]])
                    self._phrase_idx += 1
                self._neem_idx = 0
                self._scope = ShuttleScope.PHRASE

            case _:
                pass  # other loop kinds reserved for phase 2

    def _swerve(self, glyph: Petal) -> None:
        """move or rescope the shuttle"""
        from sp5n.bend import SwerveKind

        match glyph:
            case SwerveKind.BACK:
                self._swerve_back()
            case SwerveKind.FORWARD:
                self._swerve_forward()
            case SwerveKind.GROW:
                self._swerve_grow()
            case SwerveKind.SHRINK:
                self._swerve_shrink()
            case _:
                pass  # time axis and selection axis reserved

    def _swerve_back(self) -> None:
        """move shuttle to previous sibling at current scope"""
        match self._scope:
            case ShuttleScope.PETAL:
                if self._petal_idx > 0:
                    self._petal_idx -= 1
            case ShuttleScope.NEEM:
                if self._neem_idx > 0:
                    self._neem_idx -= 1
                elif self._phrase_idx > 0:
                    self._phrase_idx -= 1
                    self._neem_idx = len(self._current_phrase) - 1
            case ShuttleScope.PHRASE:
                if self._phrase_idx > 0:
                    self._phrase_idx -= 1
            case ShuttleScope.VERSE:
                pass

    def _swerve_forward(self) -> None:
        """move shuttle to next sibling at current scope"""
        match self._scope:
            case ShuttleScope.PETAL:
                neem = self._current_neem
                if self._petal_idx < len(neem) - 1:
                    self._petal_idx += 1
            case ShuttleScope.NEEM:
                phrase = self._current_phrase
                if self._neem_idx < len(phrase) - 1:
                    self._neem_idx += 1
                elif self._phrase_idx < len(self.verse) - 1:
                    self._phrase_idx += 1
                    self._neem_idx = 0
            case ShuttleScope.PHRASE:
                if self._phrase_idx < len(self.verse) - 1:
                    self._phrase_idx += 1
            case ShuttleScope.VERSE:
                pass

    def _swerve_grow(self) -> None:
        """expand shuttle scope to parent level"""
        match self._scope:
            case ShuttleScope.PETAL:
                self._scope = ShuttleScope.NEEM
            case ShuttleScope.NEEM:
                self._scope = ShuttleScope.PHRASE
            case ShuttleScope.PHRASE:
                self._scope = ShuttleScope.VERSE
            case ShuttleScope.VERSE:
                pass

    def _swerve_shrink(self) -> None:
        """reduce shuttle scope to last child"""
        match self._scope:
            case ShuttleScope.VERSE:
                self._phrase_idx = len(self.verse) - 1
                self._scope = ShuttleScope.PHRASE
            case ShuttleScope.PHRASE:
                self._neem_idx = len(self._current_phrase) - 1
                self._scope = ShuttleScope.NEEM
            case ShuttleScope.NEEM:
                neem = self._current_neem
                if neem:
                    self._petal_idx = len(neem) - 1
                    self._scope = ShuttleScope.PETAL
            case ShuttleScope.PETAL:
                pass

    def _yank(self, glyph: Petal) -> None:
        """remove or manipulate content at the shuttle"""
        from sp5n.bend import YankKind

        match glyph:
            case YankKind.DELETE:
                self._delete_at_shuttle()
            case _:
                pass  # scratch buffer reserved for phase 2

    def _delete_at_shuttle(self) -> None:
        """remove content at the shuttle based on current scope"""
        match self._scope:
            case ShuttleScope.PETAL:
                self._delete_petal()
            case ShuttleScope.NEEM:
                self._delete_neem()
            case ShuttleScope.PHRASE:
                self._delete_phrase()
            case ShuttleScope.VERSE:
                self._delete_verse()

    def _delete_petal(self) -> None:
        """remove the petal at _petal_idx"""
        neem = self._current_neem
        if not neem:
            return

        del neem[self._petal_idx]

        if not neem:
            # last petal removed — scope goes to neem
            self._petal_idx = 0
            self._scope = ShuttleScope.NEEM
        elif self._petal_idx >= len(neem):
            self._petal_idx = len(neem) - 1

    def _delete_neem(self) -> None:
        """remove the neem at the shuttle and adjust position"""
        phrase = self._current_phrase

        if len(self.verse) == 1 and len(phrase) == 1:
            # last neem in last phrase — clear it, don't remove
            phrase[0] = []
            return

        del phrase[self._neem_idx]

        if not phrase:
            # phrase is now empty — remove it too
            del self.verse[self._phrase_idx]
            if self._phrase_idx > 0:
                self._phrase_idx -= 1
            self._neem_idx = len(self._current_phrase) - 1
        elif self._neem_idx >= len(phrase):
            self._neem_idx = len(phrase) - 1

    def _delete_phrase(self) -> None:
        """remove the entire phrase at the shuttle"""
        if len(self.verse) == 1:
            # last phrase — clear to empty scaffold
            self.verse[0] = [[]]
            self._neem_idx = 0
            self._scope = ShuttleScope.NEEM
            return

        del self.verse[self._phrase_idx]
        if self._phrase_idx >= len(self.verse):
            self._phrase_idx = len(self.verse) - 1
        self._neem_idx = len(self._current_phrase) - 1

    def _delete_verse(self) -> None:
        """clear the entire verse to empty scaffold"""
        self.verse.clear()
        self.verse.append([[]])
        self._phrase_idx = 0
        self._neem_idx = 0
        self._petal_idx = 0
        self._scope = ShuttleScope.NEEM

    def _neem_start_col(self) -> int:
        """find the column where the current neem starts in rendered phrase"""
        phrase = self._current_phrase
        col = 0
        for n_idx, n in enumerate(phrase):
            if n_idx == self._neem_idx:
                break
            if n:  # empty neems skipped in rendering
                col += len(render_neem(n)) + 1  # +1 for space
        return col

    def _compute_shuttle(
        self, phrase_start_lines: list[int], rendered_lines: list[str]
    ) -> tuple[tuple[int, int, int], ...]:
        """compute shuttle highlight segments in rendered output"""
        match self._scope:
            case ShuttleScope.PETAL:
                return self._compute_shuttle_petal(phrase_start_lines)
            case ShuttleScope.NEEM:
                return self._compute_shuttle_neem(phrase_start_lines)
            case ShuttleScope.PHRASE:
                return self._compute_shuttle_phrase(
                    phrase_start_lines, rendered_lines
                )
            case ShuttleScope.VERSE:
                return self._compute_shuttle_verse(rendered_lines)

    def _compute_shuttle_petal(
        self, phrase_start_lines: list[int]
    ) -> tuple[tuple[int, int, int], ...]:
        """highlight single petal character"""
        neem = self._current_neem
        if not neem:
            # edge case: shouldn't be at petal scope with empty neem
            col = self._neem_start_col()
            base_line = phrase_start_lines[self._phrase_idx]
            line = base_line + col // self.panel_width
            col_in_line = col % self.panel_width
            return ((line, col_in_line, col_in_line),)

        col = self._neem_start_col() + self._petal_idx
        base_line = phrase_start_lines[self._phrase_idx]
        line = base_line + col // self.panel_width
        col_in_line = col % self.panel_width
        return ((line, col_in_line, col_in_line + 1),)

    def _compute_shuttle_neem(
        self, phrase_start_lines: list[int]
    ) -> tuple[tuple[int, int, int], ...]:
        """highlight entire neem"""
        neem = self._current_neem
        col = self._neem_start_col()
        neem_len = len(render_neem(neem))
        start = col
        end = col + neem_len

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
            return (
                (start_line, start_col, self.panel_width),
                (end_line, 0, end_col),
            )

    def _compute_shuttle_phrase(
        self,
        phrase_start_lines: list[int],
        rendered_lines: list[str],
    ) -> tuple[tuple[int, int, int], ...]:
        """highlight entire phrase across all lines it spans"""
        phrase_line = phrase_start_lines[self._phrase_idx]
        if self._phrase_idx + 1 < len(phrase_start_lines):
            end_line = phrase_start_lines[self._phrase_idx + 1]
        else:
            end_line = len(rendered_lines)

        segments: list[tuple[int, int, int]] = []
        for ln in range(phrase_line, min(end_line, self.panel_height)):
            line_len = (
                len(rendered_lines[ln]) if ln < len(rendered_lines) else 0
            )
            segments.append((ln, 0, max(line_len, 0)))

        if not segments:
            return ((phrase_line, 0, 0),)
        return tuple(segments)

    def _compute_shuttle_verse(
        self, rendered_lines: list[str]
    ) -> tuple[tuple[int, int, int], ...]:
        """highlight all content in the verse"""
        segments: list[tuple[int, int, int]] = []
        for ln, line in enumerate(rendered_lines):
            if ln >= self.panel_height:
                break
            segments.append((ln, 0, len(line)))

        if not segments:
            return ((0, 0, 0),)
        return tuple(segments)

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

        shuttle = self._compute_shuttle(phrase_start_lines, lines)

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
