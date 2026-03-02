"""
hexes: curses tui for charkha

plays both wheel (keyboard input) and display (panel rendering) roles

input is handled by evdev in a reader thread; curses is used only for
terminal display. a thread-safe queue bridges the two.

the evdev reader is stateless — it sends raw key events on the queue.
the main loop owns key state and calls spin().

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

exit with enter+Q (cant-quit) or ctrl-c
"""

import curses
import queue
import threading
from typing import Final

import evdev
import evdev.ecodes as ec

from charkha.bend import BendKind, CantKind
from charkha.tape import PocketLoom
from charkha.wheel import (
    Key,
    KeyState,
    SpinError,
    current_chord,
    spin,
)

# minimum terminal size
MIN_WIDTH = 20
MIN_HEIGHT = 4

# height of the debug strip at the bottom
DEBUG_HEIGHT = 1

# --- evdev-to-charkha key mapping ---

_EVDEV_KEY_MAP: Final[dict[int, Key]] = {
    ec.KEY_Q: "qQ",
    ec.KEY_W: "wW",
    ec.KEY_E: "eE",
    ec.KEY_R: "rR",
    ec.KEY_T: "tT",
    ec.KEY_Y: "yY",
    ec.KEY_U: "uU",
    ec.KEY_I: "iI",
    ec.KEY_O: "oO",
    ec.KEY_P: "pP",
    ec.KEY_LEFTBRACE: "[{",
    ec.KEY_A: "aA",
    ec.KEY_S: "sS",
    ec.KEY_D: "dD",
    ec.KEY_F: "fF",
    ec.KEY_G: "gG",
    ec.KEY_H: "hH",
    ec.KEY_J: "jJ",
    ec.KEY_K: "kK",
    ec.KEY_L: "lL",
    ec.KEY_SEMICOLON: ";:",
    ec.KEY_APOSTROPHE: "'\"",
    ec.KEY_Z: "zZ",
    ec.KEY_X: "xX",
    ec.KEY_C: "cC",
    ec.KEY_V: "vV",
    ec.KEY_B: "bB",
    ec.KEY_N: "nN",
    ec.KEY_M: "mM",
    ec.KEY_COMMA: ",<",
    ec.KEY_DOT: ".>",
    ec.KEY_SLASH: "/?",
    ec.KEY_ENTER: "enter",
    ec.KEY_SPACE: "space",
    ec.KEY_LEFTSHIFT: "left-shift",
    ec.KEY_RIGHTSHIFT: "right-shift",
}


def _find_keyboard() -> evdev.InputDevice:
    """find the first input device with a full alpha key range

    looks for a device that reports KEY_Q through KEY_P (top row).
    raises RuntimeError if no keyboard is found.
    """
    alpha_top = {
        ec.KEY_Q,
        ec.KEY_W,
        ec.KEY_E,
        ec.KEY_R,
        ec.KEY_T,
        ec.KEY_Y,
        ec.KEY_U,
        ec.KEY_I,
        ec.KEY_O,
        ec.KEY_P,
    }
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities()
        keys = caps.get(ec.EV_KEY, [])
        # a real keyboard has alpha keys and LED indicators (caps/num
        # lock) but no relative axes (mice report alpha keys too for
        # programmable buttons)
        if (
            alpha_top.issubset(keys)
            and ec.EV_LED in caps
            and ec.EV_REL not in caps
        ):
            return dev
    raise RuntimeError(
        "no keyboard found - check /dev/input permissions "
        "and input group membership"
    )


def _evdev_reader(
    device: evdev.InputDevice,
    key_queue: "queue.Queue[tuple[Key, bool]]",
) -> None:
    """read evdev events and forward mapped key events on the queue

    stateless. runs in a daemon thread. sends (Key, pressed) tuples.
    """
    for event in device.read_loop():
        if event.type != ec.EV_KEY:
            continue

        # value: 0=release, 1=press, 2=repeat (ignored)
        if event.value == 2:
            continue

        charkha_key = _EVDEV_KEY_MAP.get(event.code)
        if charkha_key is None:
            continue

        key_queue.put((charkha_key, event.value == 1))


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
    shuttle: tuple[tuple[int, int, int], ...],
    height: int,
    width: int,
) -> None:
    """draw the verse panel with shuttle highlight"""
    win.erase()
    for i, line in enumerate(lines[:height]):
        try:
            win.addstr(i, 0, line[:width])
        except curses.error:
            pass

    # apply shuttle highlight (inverse video)
    for line_num, start_col, end_col in shuttle:
        if line_num >= height:
            continue
        if start_col == end_col:
            # empty neem — show cursor as inverse space
            try:
                win.addstr(line_num, start_col, " ", curses.A_REVERSE)
            except curses.error:
                pass
        else:
            text = lines[line_num][start_col:end_col]
            try:
                win.addstr(line_num, start_col, text, curses.A_REVERSE)
            except curses.error:
                pass

    win.noutrefresh()


def run(stdscr: "curses.window") -> None:
    """main loop - called by curses.wrapper"""
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
    key_state: KeyState = frozenset()

    # initial render
    panel = loom.render()
    _draw_verse(verse_win, panel.lines, panel.shuttle, verse_height, width)
    _draw_debug(debug_win, chord_indicator, glyph_history, width)
    curses.doupdate()

    # find keyboard and start evdev reader thread
    device = _find_keyboard()
    key_queue: queue.Queue[tuple[Key, bool]] = queue.Queue()
    reader = threading.Thread(
        target=_evdev_reader,
        args=(device, key_queue),
        daemon=True,
    )
    reader.start()

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
                _draw_verse(
                    verse_win, panel.lines, panel.shuttle, verse_height, width
                )
                _draw_debug(
                    debug_win,
                    chord_indicator,
                    glyph_history,
                    width,
                )
                curses.doupdate()

            # drain the key event queue
            while True:
                try:
                    key, pressed = key_queue.get_nowait()
                except queue.Empty:
                    break

                try:
                    key_state, bend = spin(key_state, key, pressed)
                except SpinError:
                    key_state = key_state - {key}
                    chord_indicator = "x"
                    _draw_debug(
                        debug_win,
                        chord_indicator,
                        glyph_history,
                        width,
                    )
                    curses.doupdate()
                    continue

                chord_indicator = current_chord(key_state)

                if bend is not None:
                    # cant-quit: exit the TUI
                    if (
                        bend.kind == BendKind.CANT
                        and bend.glyph == CantKind.QUIT
                    ):
                        return

                    glyph_history += bend.glyph
                    panel = loom.push(bend)
                    _draw_verse(
                        verse_win,
                        panel.lines,
                        panel.shuttle,
                        verse_height,
                        width,
                    )

                _draw_debug(
                    debug_win,
                    chord_indicator,
                    glyph_history,
                    width,
                )
                curses.doupdate()

    except KeyboardInterrupt:
        pass


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
