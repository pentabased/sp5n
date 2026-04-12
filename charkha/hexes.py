"""
hexes: async curses tui for charkha

plays the wheel (keyboard input) and display (panel rendering) roles,
connecting to a tiraz loom server over WebTransport

input is handled by evdev async reader. display updates arrive as
petal glyph streams over a WebTransport unidirectional stream.

layout:
  top portion  - stream panel (rendered frames from tiraz)
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

import asyncio
import curses
import logging
import ssl
from typing import Final

import evdev
import evdev.ecodes as ec

from pywebtransport import (
    ClientConfig,
    WebTransportClient,
    WebTransportSession,
)

from charkha.bend import BendKind, CantKind
from charkha.wheel import (
    Key,
    KeyState,
    SpinError,
    current_chord,
    spin,
)
from charkha.wire import Display, encode_bend, decode_display

_logger = logging.getLogger(__name__)

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
    """find the first input device with a full alpha key range"""
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


# --- curses rendering ---


def _draw_debug(
    win: "curses.window", chord: str, history: str, width: int
) -> None:
    """draw the debug strip: [chord] history"""
    win.erase()
    indicator = f"[{chord}]"
    hist_width = max(0, width - len(indicator) - 1)
    tail = history[-hist_width:] if hist_width > 0 else ""
    line = f"{indicator} {tail}"
    try:
        win.addstr(0, 0, line[:width])
    except curses.error:
        pass
    win.noutrefresh()


def _draw_frames(
    win: "curses.window",
    display: Display,
    height: int,
    width: int,
) -> None:
    """draw all frames from the display's first panel"""
    win.erase()

    if not display.panels or not display.panels[0].frames:
        win.noutrefresh()
        return

    panel = display.panels[0]
    line_offset = 0

    for frame in panel.frames:
        for i, line in enumerate(frame.lines):
            row = line_offset + i
            if row >= height:
                break
            try:
                win.addstr(row, 0, line[:width])
            except curses.error:
                pass

        # draw highlight (shuttle cursor) if present
        if frame.highlight is not None:
            for line_num, start_col, end_col in frame.highlight.segments:
                row = line_offset + line_num
                if row >= height:
                    continue
                if start_col == end_col:
                    try:
                        win.addstr(row, start_col, " ", curses.A_REVERSE)
                    except curses.error:
                        pass
                else:
                    fl = (
                        frame.lines[line_num]
                        if line_num < len(frame.lines)
                        else ""
                    )
                    text = fl[start_col:end_col]
                    try:
                        win.addstr(row, start_col, text, curses.A_REVERSE)
                    except curses.error:
                        pass

        line_offset += len(frame.lines)

    win.noutrefresh()


# --- async main ---


async def _evdev_reader(
    device: evdev.InputDevice,
    key_queue: asyncio.Queue[tuple[Key, bool]],
) -> None:
    """read evdev events asynchronously and forward to queue"""
    async for event in device.async_read_loop():
        if event.type != ec.EV_KEY:
            continue
        if event.value == 2:  # repeat, ignore
            continue
        charkha_key = _EVDEV_KEY_MAP.get(event.code)
        if charkha_key is None:
            continue
        await key_queue.put((charkha_key, event.value == 1))


async def _display_reader(
    session: WebTransportSession,
    display_queue: asyncio.Queue[Display],
) -> None:
    """read display updates from the tiraz loom over WebTransport"""
    recv_stream = await session.accept_unidirectional_stream()

    while not session.is_closed:
        try:
            # read 4-byte length prefix
            length_bytes = await recv_stream.readexactly(n=4)
            length = int.from_bytes(length_bytes, "big")

            # read the display payload
            payload = await recv_stream.readexactly(n=length)
            display = decode_display(payload)
            await display_queue.put(display)

        except Exception as e:
            _logger.debug("display reader stopped: %s", e)
            break


async def run_async(stdscr: "curses.window") -> None:
    """async main loop — connects to tiraz and runs the TUI"""
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    height, width = stdscr.getmaxyx()
    if height < MIN_HEIGHT or width < MIN_WIDTH:
        stdscr.addstr(0, 0, "terminal too small")
        stdscr.getch()
        return

    verse_height = height - DEBUG_HEIGHT
    verse_win = stdscr.subwin(verse_height, width, 0, 0)
    debug_win = stdscr.subwin(DEBUG_HEIGHT, width, verse_height, 0)

    # connect to tiraz
    config = ClientConfig(verify_mode=ssl.CERT_NONE)
    client = WebTransportClient(config=config)

    try:
        session = await client.connect(url="https://localhost:4433/wheel")
    except Exception as e:
        stdscr.addstr(0, 0, f"failed to connect to tiraz: {e}"[:width])
        stdscr.getch()
        return

    _logger.info("connected to tiraz")

    # start async tasks
    key_queue: asyncio.Queue[tuple[Key, bool]] = asyncio.Queue()
    display_queue: asyncio.Queue[Display] = asyncio.Queue()

    device = _find_keyboard()
    evdev_task = asyncio.create_task(_evdev_reader(device, key_queue))
    display_task = asyncio.create_task(_display_reader(session, display_queue))

    chord_indicator = "8"
    glyph_history = ""
    key_state: KeyState = frozenset()
    current_display: Display | None = None

    _draw_debug(debug_win, chord_indicator, glyph_history, width)
    curses.doupdate()

    try:
        while not session.is_closed:
            # wait for either a key event or a display update
            done, _pending = await asyncio.wait(
                [
                    asyncio.create_task(key_queue.get()),
                    asyncio.create_task(display_queue.get()),
                ],
                timeout=0.1,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                result = task.result()

                if isinstance(result, Display):
                    current_display = result
                    _draw_frames(
                        verse_win, current_display, verse_height, width
                    )
                    _draw_debug(
                        debug_win,
                        chord_indicator,
                        glyph_history,
                        width,
                    )
                    curses.doupdate()

                elif isinstance(result, tuple):
                    key, pressed = result

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
                        # cant-quit: exit
                        if (
                            bend.kind == BendKind.CANT
                            and bend.glyph == CantKind.QUIT
                        ):
                            # send quit to tiraz
                            session.send_datagram(data=encode_bend(bend))
                            return

                        glyph_history += bend.glyph

                        # send bend to tiraz
                        session.send_datagram(data=encode_bend(bend))

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
        evdev_task.cancel()
        display_task.cancel()
        if not session.is_closed:
            await session.close()
        await client.close()


def run(stdscr: "curses.window") -> None:
    """entry point called by curses.wrapper"""
    asyncio.run(run_async(stdscr))


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
