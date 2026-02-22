"""
hexes: curses tui for sp5n

plays both wheel (keyboard input) and display (panel rendering) roles

layout:
  top portion  - verse panel (rendered output from PocketLoom)
  bottom strip - debug bar: chord indicator + scrolling glyph history

chord indicator shows current mode as a single highlighted glyph:
  8  bloom  (no chord - default)
  7  loop   (space held)
  y  yank   (left-shift held)
  c  swerve (right-shift held)
  k  cant   (enter held)
  x  error  (invalid key combination)

exit with ctrl-c
"""

import curses
import curses.ascii

from sp5n.bend import Bend
from sp5n.tape import PocketLoom
from sp5n.wheel import (
    EventKind,
    Key,
    SpinError,
    glyph_key_map,
    spin,
)

# minimum terminal size
MIN_WIDTH = 20
MIN_HEIGHT = 4

# height of the debug strip at the bottom
DEBUG_HEIGHT = 1


def _curses_key_to_sp5n(ch: int) -> tuple[Key, Key | None] | None:
    """
    map a curses character code to an (optional chord key, glyph key) pair

    returns None if the character is not a recognized sp5n key

    curses gives us the final character so we infer chord state from it:
    - enter  → cant chord, null glyph
    - space  → loop chord, null glyph
    - shift is detected from uppercase / shifted punctuation in the glyph map
    """
    # enter → cant chord with null glyph
    if ch in (curses.KEY_ENTER, ord("\n"), ord("\r")):
        return ("enter", "[{")

    # space → loop chord with null glyph
    if ch == ord(" "):
        return ("space", "[{")

    # ctrl-c → signal exit (handled by caller)
    if ch == curses.ascii.ETX:
        return None

    # try to match the character against all glyph keys
    char = chr(ch) if 0 <= ch <= 127 else None
    if char is None:
        return None

    for key, petal in glyph_key_map.items():
        if char in key:
            return (None, key)  # type: ignore[return-value]

    return None


def _infer_chord_indicator(ch: int) -> str:
    """
    return the chord indicator glyph for the current character
    used to update the static chord display before a bend is emitted
    """
    if ch in (curses.KEY_ENTER, ord("\n"), ord("\r")):
        return "k"
    if ch == ord(" "):
        return "7"
    # check if it's an uppercase / shifted glyph key - no chord in sp5n
    return "8"


def _draw_debug(
    win: "curses.window", chord: str, history: str, width: int
) -> None:
    """draw the debug strip: [chord] history"""
    win.erase()
    indicator = f"[{chord}]"
    # available width for history after indicator + space
    hist_width = max(0, width - len(indicator) - 1)
    # show the tail of history that fits
    tail = history[-hist_width:] if hist_width > 0 else ""
    line = f"{indicator} {tail}"
    try:
        win.addstr(0, 0, line[:width])
    except curses.error:
        pass
    win.noutrefresh()


def _draw_verse(
    win: "curses.window", lines: tuple[str, ...], height: int, width: int
) -> None:
    """draw the verse panel"""
    win.erase()
    for i, line in enumerate(lines[:height]):
        try:
            win.addstr(i, 0, line[:width])
        except curses.error:
            pass
    win.noutrefresh()


def run(stdscr: "curses.window") -> None:
    """main loop - called by curses.wrapper"""
    curses.curs_set(0)
    stdscr.nodelay(False)

    height, width = stdscr.getmaxyx()

    if height < MIN_HEIGHT or width < MIN_WIDTH:
        stdscr.addstr(0, 0, "terminal too small")
        stdscr.getch()
        return

    verse_height = height - DEBUG_HEIGHT
    loom = PocketLoom(panel_width=width, panel_height=verse_height)

    # create sub-windows
    verse_win = stdscr.subwin(verse_height, width, 0, 0)
    debug_win = stdscr.subwin(DEBUG_HEIGHT, width, verse_height, 0)

    # curses color for the chord indicator highlight
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    chord_indicator = "8"  # default: bloom mode
    glyph_history = ""

    # initial render
    panel = loom.render()
    _draw_verse(verse_win, panel.lines, verse_height, width)
    _draw_debug(debug_win, chord_indicator, glyph_history, width)
    curses.doupdate()

    while True:
        ch = stdscr.getch()

        # exit on ctrl-c
        if ch == curses.ascii.ETX:
            break

        # handle terminal resize
        if ch == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()
            verse_height = height - DEBUG_HEIGHT
            loom.panel_width = width
            loom.panel_height = verse_height
            verse_win.resize(verse_height, width)
            debug_win.mvwin(verse_height, 0)
            debug_win.resize(DEBUG_HEIGHT, width)
            panel = loom.render()
            _draw_verse(verse_win, panel.lines, verse_height, width)
            _draw_debug(debug_win, chord_indicator, glyph_history, width)
            curses.doupdate()
            continue

        # update chord indicator before processing
        chord_indicator = _infer_chord_indicator(ch)

        # map curses key to sp5n keys
        key_pair = _curses_key_to_sp5n(ch)
        if key_pair is None:
            _draw_debug(debug_win, chord_indicator, glyph_history, width)
            curses.doupdate()
            continue

        chord_key, glyph_key = key_pair

        # build inputs dict for spin()
        inputs: dict[Key, EventKind] = {}
        if chord_key is not None:
            inputs[chord_key] = EventKind.RELEASED
        if glyph_key is not None:
            inputs[glyph_key] = EventKind.RELEASED

        # spin the inputs into a bend
        try:
            bend: Bend | None = spin(inputs)
        except SpinError:
            chord_indicator = "x"
            _draw_debug(debug_win, chord_indicator, glyph_history, width)
            curses.doupdate()
            continue

        if bend is None:
            continue

        # update glyph history with the bend glyph
        glyph_history += bend.glyph

        # push bend to loom and get updated panel
        panel = loom.push(bend)

        # redraw
        _draw_verse(verse_win, panel.lines, verse_height, width)
        _draw_debug(debug_win, chord_indicator, glyph_history, width)
        curses.doupdate()


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
