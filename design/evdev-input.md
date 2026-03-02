# replace pynput with evdev for keyboard input

supersedes: pynput-input.md

## context

pynput's xorg backend is silently broken under Wayland - it connects to
XWayland but receives zero key events because Wayland compositors block
XWayland apps from global keyboard monitoring. pynput's uinput backend
exists but is poorly documented and adds unnecessary abstraction.

evdev reads directly from `/dev/input/eventN` via the Linux kernel input
subsystem. it requires the user to be in the `input` group (already done)
and has no dependency on X11 or Wayland. it's already installed as a
pynput dependency.

we confirmed evdev works: press/release events with proper keycodes come
through cleanly on `/dev/input/event3` (AT Translated Set 2 keyboard).

## decision

replace pynput with evdev for all keyboard input. curses stays for
terminal rendering. same threading model as before - an evdev reader
thread puts events on a queue, the curses main loop drains it.

### changes

**pyproject.toml** - replace `pynput>=1.7.7` with `evdev>=1.9`

**charkha/hexes.py** - rewrite input handling:
- remove all pynput imports, `_ensure_maps()`, `_pynput_to_charkha()`,
  and the lazy `_special_map`/`_char_map` globals
- add `_EVDEV_KEY_MAP` dict mapping `evdev.ecodes.KEY_*` constants to
  charkha `Key` literals (KEY_Q → "qQ", KEY_SPACE → "space", etc.)
- add `_find_keyboard()` function that scans `/dev/input/` for the first
  device with a full alpha key range (KEY_Q..KEY_P at minimum)
- rewrite `KeyStateTracker` to accept evdev `InputEvent` objects:
  - value 1 = press, value 0 = release, value 2 = OS repeat (ignored)
  - on press: translate keycode, add to pressed set, update chord indicator
  - on release: translate keycode, build inputs dict, call spin()
  - ctrl-c detection via KEY_LEFTCTRL held + KEY_C released
- add `_evdev_reader()` function that runs in a daemon thread:
  - reads events in a blocking loop (no grab needed)
  - translates EV_KEY events and puts them on the queue
- rewrite `run()` to start the evdev reader thread instead of pynput Listener

**no changes** to `wheel.py`, `bend.py`, `tape.py`, `petal.py`, `time.py`

### threading model

same shape as the pynput version - only the input source changes:

```
evdev reader thread (blocking)       curses main thread (50ms poll)
  device.read_loop()                   getch() → only KEY_RESIZE
         |                                  |
    filter EV_KEY events              drain queue
    translate keycode                 update pressed-key set
         |                            filter OS repeat
    queue.put(                        call spin() on release
      ("press", key) or               push bends → loom → render
      ("release", key)                update chord indicator
    )  ──────────────────────►        curses.doupdate()
```

### keyboard device detection

rather than hardcoding `/dev/input/event3`, scan all input devices and
pick the first one that reports KEY_Q through KEY_P (the top alpha row).
this handles external keyboards and different device numbering.

### grab behavior

we do NOT grab the keyboard. evdev can read events non-exclusively -
the compositor and other apps continue to receive keyboard input as
normal. this means screenshots, window switching, and other system
shortcuts keep working while the TUI is running.

ctrl-c is handled both by the compositor (raises KeyboardInterrupt in
the curses main thread) and internally (KEY_LEFTCTRL + KEY_C sends
"quit" on the queue). both paths exit cleanly.

## consequences

**good:**
- works on Wayland, X11, and headless TTY - anywhere `/dev/input` exists
- no X11/Wayland dependency at all
- proper press/release/repeat events with keycodes
- evdev is a thin wrapper over the kernel interface - minimal abstraction
- one fewer dependency (drop pynput, keep evdev which was already installed)

**limitations (acceptable for prototype):**
- Linux only (evdev is a Linux kernel interface)
- requires `input` group membership
- hardcoded to first detected keyboard device (fine for now)
