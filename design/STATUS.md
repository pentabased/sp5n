# sp5n status

last updated: 2026-02-22

## what works

- **petal, time, bend, wheel** - ported from v0, 60 tests passing
- **tape** - PocketLoom accepts bends, maintains a verse, renders panels
  - bloom (typing petals), loop-neem (space), loop-phrase (space+p)
  - swerve back/forward between neems
  - nope (enter alone) removes last petal from current neem
- **hexes** - curses TUI with evdev keyboard input
  - evdev reads directly from /dev/input (works on Wayland)
  - auto-detects keyboard device (filters out mice by checking EV_LED)
  - chord indicator and glyph history in debug bar
  - `just run` opens the TUI, ctrl-c to exit

## what we just did

- replaced pynput with evdev for keyboard input
  - pynput's xorg backend silently broken under Wayland (zero events)
  - evdev reads kernel input events directly, requires `input` group
  - debugged device detection: Logitech mouse reports alpha keycodes,
    fixed by requiring EV_LED and excluding EV_REL
- design docs: evdev-input.md, pynput-input.md marked superseded
- removed keyboard grab (`device.grab()`) - evdev reads non-exclusively
  so the compositor keeps receiving input (screenshots, etc. work)

## what's next

- **shuttle cursor display** - the loom tracks shuttle position but
  there's no visual feedback in the TUI. this is the foundation for
  both swerve (navigation) and yank (selection/deletion). needs a
  design doc before implementation.
- **yank functionality** - delete/cut/copy/paste at neem level and above
- **phoneme reference** - some kind of overlay or cheatsheet for the
  glyph-to-phoneme mapping while building muscle memory

## open questions

- how should the shuttle cursor look? inverse video on the current neem?
  underline? bracket markers?
- should nope (undo) cross neem boundaries? currently it only removes
  petals from the current neem. yank-delete would handle removing whole
  neems but that's not implemented yet.
