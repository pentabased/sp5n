# replace curses keyboard input with pynput

## context

the curses `getch()` model only gives us the final character after modifier
processing - we can't detect "space held while p is pressed" to emit a
loop-phrase bend, and we can't distinguish press from hold from release.
this blocks chord-based input (loop, swerve, yank, cant).

pynput provides per-key press/release edge events via an X11 listener thread,
which is exactly what `spin()` in `wheel.py` was designed to consume. we keep
curses for terminal display only.

## decision

use pynput's keyboard Listener for all input. curses stays for rendering.
a thread-safe queue bridges the pynput listener thread to the curses main loop.

### changes

**pyproject.toml** - add `pynput>=1.7.7` to dependencies

**sp5n/hexes.py** - rewrite input handling:
- remove `_curses_key_to_sp5n()` and `_infer_chord_indicator()`
- add `_pynput_to_sp5n(key)` to map pynput key objects to sp5n `Key` literals
- add `KeyStateTracker` class that tracks pressed keys, filters OS repeat,
  builds `inputs` dicts for `spin()`, and puts bends on the queue
- rewrite `run()` to poll the queue from the curses main loop (50ms timeout)
- `getch()` only used for `KEY_RESIZE`

**no changes** to `wheel.py`, `bend.py`, `tape.py`, `petal.py`, `time.py`

### threading model

the pynput listener thread should be as thin as possible: just translate
pynput key objects to sp5n Key literals and put raw press/release edge
events on the queue. all mutable state (the pressed-key set, spin() calls,
loom updates, curses rendering) lives on the main thread.

this avoids needing a lock to protect shared state between threads - the
queue is the only communication channel and it handles thread-safety
internally.

```
pynput Listener thread              curses main thread (50ms poll)
  on_press / on_release               getch() → only KEY_RESIZE
         |                                  |
    translate to sp5n Key              drain queue
         |                            update pressed-key set
    queue.put(                        filter OS repeat
      ("press", key) or               call spin() on release
      ("release", key)                push bends → loom → render
    )  ──────────────────────►        update chord indicator
                                      curses.doupdate()
```

## consequences

**good:**
- proper chord detection - hold space + tap p gives loop-phrase (new line)
- no OS key repeat - only edge events
- `spin()` finally receives the press/hold/release model it was designed for
- clean separation: pynput = input, curses = output

**limitations (acceptable for prototype):**
- pynput captures keys globally, not just when the terminal is focused
- requires X11 on Linux (no pure Wayland or headless TTY)
- curses `getch()` may also see keystrokes - we ignore all non-resize returns
- this is a prototype; the plan is to rewrite everything in rust eventually

## verification

1. `just init` to install pynput
2. `just test` - all 60 existing tests pass unchanged
3. `just validate` - format, typecheck, tests all clean
4. `just run` - type glyphs; space for new neem; hold space + p for new phrase;
   enter for nope/undo; ctrl-c to exit
5. chord indicator shows live state (updates when chord key is held)
