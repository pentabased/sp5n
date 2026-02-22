"""
hexes: curses tui for sp5n

plays both wheel (keyboard input) and display (panel rendering) roles

input is handled by pynput in a listener thread; curses is used only for
terminal display. a thread-safe queue bridges the two.

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
import queue
import threading

from sp5n.bend import Bend
from sp5n.tape import PocketLoom
from sp5n.wheel import (
    EventKind,
    Key,
    SpinError,
    chord_key_map,
    glyph_key_map,
    spin,
)

# minimum terminal size
MIN_WIDTH = 20
MIN_HEIGHT = 4

# height of the debug strip at the bottom
DEBUG_HEIGHT = 1

# --- pynput-to-sp5n key mapping ---

# built lazily on first call to _pynput_to_sp5n()
_special_map: dict[object, Key] = {}
_char_map: dict[str, Key] = {}
_maps_initialized = False


def _ensure_maps() -> None:
    """build the pynput-to-sp5n lookup tables on first use"""
    global _maps_initialized
    if _maps_initialized:
        return

    from pynput.keyboard import Key as PynputKey

    _special_map[PynputKey.enter] = "enter"
    _special_map[PynputKey.space] = "space"
    _special_map[PynputKey.shift] = "left-shift"
    _special_map[PynputKey.shift_l] = "left-shift"
    _special_map[PynputKey.shift_r] = "right-shift"

    for sp5n_key in glyph_key_map:
        for ch in sp5n_key:
            _char_map[ch] = sp5n_key

    _maps_initialized = True


def _pynput_to_sp5n(key: object) -> Key | None:
    """map a pynput key to an sp5n Key literal, or None if unmapped"""
    from pynput.keyboard import Key as PynputKey, KeyCode

    _ensure_maps()

    if isinstance(key, PynputKey):
        return _special_map.get(key)

    if isinstance(key, KeyCode) and key.char is not None:
        return _char_map.get(key.char)

    return None


def _current_chord(pressed: set[Key]) -> str:
    """return the chord indicator glyph for the currently held keys"""
    for chord_key, bend_kind in chord_key_map.items():
        if chord_key in pressed:
            return bend_kind.value
    return "8"  # bloom (no chord)


class KeyStateTracker:
    """tracks key press/release state and emits bends via a queue

    runs in the pynput listener thread. keeps a set of currently-pressed
    sp5n keys, filters OS key repeat, and calls spin() on each release.
    """

    def __init__(self, bend_queue: queue.Queue[tuple[str, object]]) -> None:
        self._pressed: set[Key] = set()
        self._queue = bend_queue
        self._lock = threading.Lock()

    def on_press(self, key: object) -> None:
        from pynput.keyboard import KeyCode

        # ctrl-c detection
        if isinstance(key, KeyCode) and key.char == "\x03":
            self._queue.put(("quit", None))
            return

        sp5n_key = _pynput_to_sp5n(key)
        if sp5n_key is None:
            return

        with self._lock:
            if sp5n_key in self._pressed:
                return  # filter OS key repeat
            self._pressed.add(sp5n_key)
            indicator = _current_chord(self._pressed)

        self._queue.put(("chord", indicator))

    def on_release(self, key: object) -> None:
        sp5n_key = _pynput_to_sp5n(key)
        if sp5n_key is None:
            return

        with self._lock:
            self._pressed.discard(sp5n_key)

            # build inputs: held keys as HELD, released key as RELEASED
            inputs: dict[Key, EventKind] = {}
            for held_key in self._pressed:
                inputs[held_key] = EventKind.HELD
            inputs[sp5n_key] = EventKind.RELEASED

            indicator = _current_chord(self._pressed)

        # call spin outside the lock (pure function on the snapshot)
        try:
            bend = spin(inputs)
        except SpinError:
            self._queue.put(("error", None))
            self._queue.put(("chord", indicator))
            return

        if bend is not None:
            self._queue.put(("bend", bend))
        self._queue.put(("chord", indicator))


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
    win: "curses.window",
    lines: tuple[str, ...],
    height: int,
    width: int,
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
    from pynput.keyboard import Listener

    curses.curs_set(0)
    stdscr.timeout(50)  # 50ms poll for queue + resize

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

    # start pynput listener
    bend_queue: queue.Queue[tuple[str, object]] = queue.Queue()
    tracker = KeyStateTracker(bend_queue)
    listener = Listener(
        on_press=tracker.on_press, on_release=tracker.on_release
    )
    listener.start()

    try:
        while True:
            # poll curses for terminal resize only
            ch = stdscr.getch()
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
                _draw_debug(
                    debug_win,
                    chord_indicator,
                    glyph_history,
                    width,
                )
                curses.doupdate()

            # drain the bend queue
            while True:
                try:
                    tag, payload = bend_queue.get_nowait()
                except queue.Empty:
                    break

                if tag == "quit":
                    return

                if tag == "error":
                    chord_indicator = "x"
                    _draw_debug(
                        debug_win,
                        chord_indicator,
                        glyph_history,
                        width,
                    )
                    curses.doupdate()

                elif tag == "chord":
                    assert isinstance(payload, str)
                    chord_indicator = payload
                    _draw_debug(
                        debug_win,
                        chord_indicator,
                        glyph_history,
                        width,
                    )
                    curses.doupdate()

                elif tag == "bend":
                    assert isinstance(payload, Bend)
                    glyph_history += payload.glyph
                    panel = loom.push(payload)
                    _draw_verse(verse_win, panel.lines, verse_height, width)
                    _draw_debug(
                        debug_win,
                        chord_indicator,
                        glyph_history,
                        width,
                    )
                    curses.doupdate()

    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
