# charkha implementation plan

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

**charkha.petal**

port from v0 - solid and well-tested, minor cleanup only

- `Petal` - literal type for the 32 glyph characters
- `Bloom` - a sequence of 1-32 petals with bidirectional int conversion
- `Word` - exactly 13 petals (63-64 bits signed), for identifiers and hashes
- `petal_value` - dict mapping glyph → 0-31
- `petal_order` - tuple mapping 0-31 → glyph

**charkha.time**

port from v0 with constructor bug fixed (self._seconds_since_epoch vs self._seconds)

- `Time` - 39-bit signed integer (seconds since unix epoch), converts to/from 8-petal stamp
- `Stamp` - type alias for tuple of 8 petals

**charkha.bend**

port and clean up from v0 - align terminology with current spec

- `Bend` - a frozen dataclass with two `Petal` fields: `kind` + `glyph`
  (10 bits total, suitable for compact serialization)
- `BendKind` - StrEnum: BLOOM(`8`) / LOOP(`7`) / YANK(`y`) / SWERVE(`c`) / CANT(`k`)
- sub-kind enums (StrEnum values are valid Petals, used for validation
  and pattern matching):
  - `CantKind` - SUGGEST(`-`) / THUMP(`2`) / QUIT(`Q`)
  - `SwerveKind` - four axes, nine glyphs (see tape-documents.md)
  - `YankKind` - DELETE(`-`) for phase 1; scratch buffer actions in phase 2
  - `LoopKind` - NEEM(`-`) / PHRASE(`p`) / VERSE(`v`)
- glyph frozensets (`cant_glyphs`, `swerve_glyphs`, etc.) derived from enums

**charkha.wheel**

port from v0, redesigned to own key state tracking

- `Key` - literal type for all physical key names
- `KeyState` - `frozenset[Key]` of currently pressed keys
- `glyph_key_map` - physical key names → petals
- `chord_key_map` - chord key names → petal values (not BendKind)
- `spin(state, key, pressed)` - takes key state + event, returns
  `(new_state, Bend | None)`. emits bends on falling edges only.
- `current_chord(state)` - returns the chord petal for display
- `_evaluate(inputs)` - private; validates key combination and builds Bend

**charkha.tape**

tape document node types + minimal in-process loom stub

node types for phase 1 (just the three needed for a single verse):
- `Neem` - a sequence of petals evoking a single word
- `Phrase` - a sequence of neems evoking a thought
- `Verse` - a sequence of phrases developing a theme

`Panel` - a frozen dataclass: width, height, tuple of strings

`PocketLoom` - accepts bends, maintains a single in-progress verse,
emits panels. the shuttle cursor is a `(phrase_idx, neem_idx)` position:
- bloom bends → append petal to current neem
- loop + NEEM → start a new neem in the current phrase
- loop + PHRASE → start a new phrase in the current verse
- swerve bends → move shuttle position within the verse (back/forward/
  grow/shrink; undo/redo and scoop/stretch reserved for phase 2)
- yank + DELETE → remove node at shuttle scope, shuttle moves to
  previous sibling (see tape-documents.md for full semantics)
- cant → suggest reserved for future loom integration
- cant + QUIT → handled in hexes main loop (exit TUI)

rendering: the loom maps each phrase to a line of rendered text,
wrapping neems with spaces, and packs lines into a panel sized to
the terminal window

**charkha.hexes**

curses TUI with evdev keyboard input

- evdev reader thread is fully stateless — sends `(Key, bool)` tuples
  on a thread-safe queue
- main loop owns `KeyState` and calls `spin()` / `current_chord()`
- passes bends to `PocketLoom`, renders panels to curses
- debug bar: chord indicator + scrolling glyph history
- exit via cant-quit (enter+Q) or ctrl-c

### milestone

`just run` opens a curses terminal where:

1. the 32 glyph keys + 4 chord keys produce bends
2. the current verse is rendered as phonetic text in a panel
3. swerve navigates the shuttle, yank-delete removes content
4. a debug bar shows chord indicator + raw petal input stream

## phase 2: local server

extract loom and plaza into tiraz, connect charkha via a simple local protocol

- tiraz runs as a local process (plain http or unix socket)
- charkha.wheel streams bends to tiraz
- tiraz maintains document state, renders panels, streams them back
- charkha.hexes displays incoming panels

charkha loses `PocketLoom` and gains a thin client that speaks the tiraz protocol

## phase 3: webtransport

migrate charkha ↔ tiraz connection to http3 webtransport

this is the point where multiple wheels and multiple displays can connect to a single
tiraz instance and the collaborative loom model becomes real - including the use case
of a shared public display with participants each using a handheld wheel

## porting notes from v0

all ports complete:

- `petal.py` → `charkha.petal` - ported as-is, tests pass
- `wheel.py` → `charkha.wheel` - ported, redesigned with `KeyState` and
  falling-edge `spin()` signature
- `bend.py` → `charkha.bend` - ported, `Bend` now takes two `Petal` values
  (frozen dataclass), sub-kind enums are StrEnums with Petal values
- `time.py` → `charkha.time` - ported with constructor bug fix
- `loom.py` → not ported; redesigned as `charkha.tape` (`PocketLoom`)
