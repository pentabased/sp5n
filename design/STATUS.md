# sp5n status

last updated: 2026-02-28

## what works

- **petal, time, bend, wheel** — core input model, 75 tests passing
- **bend** — frozen dataclass with two Petal fields (kind + glyph, 10 bits)
  - BendKind, CantKind, SwerveKind, YankKind, LoopKind as StrEnums
  - swerve has four axes: scope (W/S), tree (A/D), time (Z/X/C), selection (Q/E)
  - yank phase 1: DELETE only (null glyph, left-shift alone)
  - cant: SUGGEST reserved for loom suggestions, THUMP, QUIT
- **tape** — PocketLoom accepts bends, maintains a verse, renders panels
  - bloom (typing petals), loop-neem (space), loop-phrase (space+p)
  - swerve back/forward between neems and phrases
  - yank-delete removes neem at shuttle, adjusts position
  - shuttle cursor position computed during render(), included in Panel
  - Panel carries shuttle highlight as (line, start_col, end_col) segments
- **hexes** — curses TUI with evdev keyboard input
  - evdev reads directly from /dev/input (works on Wayland)
  - auto-detects keyboard device (filters out mice by checking EV_LED)
  - chord indicator and glyph history in debug bar
  - shuttle cursor displayed as inverse video on current neem
  - `just run` opens the TUI, cant-quit (enter+Q) or ctrl-c to exit

## what we just did

- finalized swerve design with four axes (scope, tree, time, selection)
  - binary time tree model: undo/redo-left/redo-right navigates edit history
  - WASD-style layout under left hand with right-shift chord
- replaced nope cant with suggest (reserved for accepting loom suggestions)
- implemented phase 1 yank-delete at shuttle (neem) scope
- implemented shuttle cursor visualization
  - loom computes shuttle position during render()
  - Panel carries shuttle segments for display
  - hexes applies inverse video (curses.A_REVERSE) at shuttle position
  - handles zero-width cursors (empty neems) and line wrapping
- design docs: shuttle-visualization.md, updated tape-documents.md

## what's next

- **revisit yank scope** — yank-delete currently operates at neem level;
  may want petal-level delete or scope-aware behavior
- **time axis implementation** — swerve undo/redo keys mapped but edit
  history tree not yet built in the loom
- **phoneme reference** — some kind of overlay or cheatsheet for the
  glyph-to-phoneme mapping while building muscle memory
- **phase 2 yank** — scratch buffer for copy/cut/paste operations
  using right-hand keys with left-shift chord

## open questions

- should yank-delete also work at petal scope (removing last petal)?
  or is that what undo (swerve time axis) should handle?
- scratch buffer design for phase 2 yank — how should scoop/paste
  interact with the shuttle scope?
