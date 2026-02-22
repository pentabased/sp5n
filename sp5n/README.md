# sp5n implementation plan

## north star for phase 1

type a verse on a 40% keyboard and see it rendered in the terminal

a verse is the smallest branch node in the tape document scheme - a series of phrases developing a theme

## four-component model

even in phase 1 with everything in a single process, the architecture follows four distinct roles:

```
┌────────┐  bends   ┌──────┐  panels  ┌─────────┐
│ wheel  │ ───────► │      │ ───────► │ display │
└────────┘          │ loom │          └─────────┘
                    │      │  screeds  ┌────────┐
                    └──────┘ ◄───────► │ plaza  │
                                       └────────┘
```

- **wheel** - keyboard input only; emits bends; knows nothing about documents
- **loom** - owns all document state and rendering; accepts bends; emits panels
- **plaza** - persists screeds; in phase 1 this is just in-memory state inside `PocketLoom`
- **display** - shows panels; knows nothing about documents

a **panel** in phase 1 is a fixed-size block of rendered text: a width, a height, and a list of strings. the loom is aware of panel dimensions and renders to fit. scrolling is out of scope for phase 1.

keeping these interfaces clean in phase 1 means phase 2 extraction is just replacing in-process calls with network calls.

## phase 1: in-process prototype

everything runs in a single python process with no networking

### modules

**sp5n.petal**

port from v0 - solid and well-tested, minor cleanup only

- `Petal` - literal type for the 32 glyph characters
- `Bloom` - a sequence of 1-32 petals with bidirectional int conversion
- `Word` - exactly 13 petals (63-64 bits signed), for identifiers and hashes
- `petal_value` - dict mapping glyph → 0-31
- `petal_order` - tuple mapping 0-31 → glyph

**sp5n.time**

port from v0 with constructor bug fixed (self._seconds_since_epoch vs self._seconds)

- `Time` - 39-bit signed integer (seconds since unix epoch), converts to/from 8-petal stamp
- `Stamp` - type alias for tuple of 8 petals

**sp5n.bend**

port and clean up from v0 - align terminology with current spec

- `BendKind` - enum: BLOOM / LOOP / YANK / SWERVE / CANT
- `Bend` - a single input event: kind + petal glyph

**sp5n.wheel**

port from v0 - input validation logic in `spin()` is clean

- `glyph_key_map` - physical key names → petals
- `chord_key_map` - chord key names → bend kinds
- `spin()` - validate key combination and emit a `Bend`

**sp5n.tape**

new - tape document node types + minimal in-process loom stub

node types for phase 1 (just the three needed for a single verse):
- `Neem` - a sequence of petals evoking a single word
- `Phrase` - a sequence of neems evoking a thought
- `Verse` - a sequence of phrases developing a theme

`Panel` - a fixed-size rendered block: width, height, list of strings

`PocketLoom` - accepts bends, maintains a single in-progress verse, emits panels:
- bloom bends → append petal to current neem
- loop + NEEM glyph → start a new neem in the current phrase
- loop + PHRASE glyph → start a new phrase in the current verse
- swerve bends → move shuttle position within the verse
- cant + null glyph (enter alone) → nope: remove the last petal from the current neem
- other cant bends → reserved for phase 2

rendering: the loom maps each phrase to a line of rendered text, wrapping neems
with spaces, and packs lines into a panel sized to the terminal window

**sp5n.hexes**

new - curses tui: plays both wheel and display roles

- capture raw key events and pass to `wheel.spin()`
- pass bends to `PocketLoom`
- receive panels from `PocketLoom` and render them to the terminal
- show a second debug panel with the raw petal stream

### milestone

`just run` opens a curses terminal where:

1. the 32 glyph keys + 4 chord keys produce bends
2. the current verse is rendered as phonetic text in a panel
3. a debug panel shows the raw petal input stream

## phase 2: local server

extract loom and plaza into 7oom, connect sp5n via a simple local protocol

- 7oom runs as a local process (plain http or unix socket)
- sp5n.wheel streams bends to 7oom
- 7oom maintains document state, renders panels, streams them back
- sp5n.hexes displays incoming panels

sp5n loses `PocketLoom` and gains a thin client that speaks the 7oom protocol

## phase 3: webtransport

migrate sp5n ↔ 7oom connection to http3 webtransport when 7oom moves to its own repo

this is the point where multiple wheels and multiple displays can connect to a single
7oom instance and the collaborative loom model becomes real - including the use case
of a shared public display with participants each using a handheld wheel

## porting notes from v0

- `petal.py` → `sp5n.petal` - port as-is, tests pass
- `wheel.py` → `sp5n.wheel` - port, clean up terminology
- `bend.py` → `sp5n.bend` - port, align `BendKind` names with current spec
- `time.py` → `sp5n.time` - port with constructor bug fix
- `loom.py` → do not port; redesign as `sp5n.tape` with loom logic staying in sp5n for phase 1, moving to 7oom in phase 2
