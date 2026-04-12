# charkha status

last updated: 2026-03-01 (session 3)

## what works

- **petal, time, bend, wheel** — core input model, 97 tests passing
- **bend** — frozen dataclass with two Petal fields (kind + glyph, 10 bits)
  - BendKind, CantKind, SwerveKind, YankKind, LoopKind as StrEnums
  - swerve has four axes: scope (W/S), tree (A/D), time (Z/X/C), selection (Q/E)
  - yank phase 1: DELETE only (null glyph, left-shift alone)
  - cant: SUGGEST reserved for loom suggestions, THUMP, QUIT
- **tape** — PocketLoom accepts bends, maintains a verse, renders panels
  - bloom (typing petals), loop-neem (space), loop-phrase (space+p)
  - shuttle has four scope levels: petal, neem, phrase, verse
  - bloom sets shuttle to petal scope (single char highlight)
  - swerve grow/shrink changes scope level (W/S keys)
  - swerve back/forward works at current scope level
  - yank-delete works at all scope levels (petal, neem, phrase, verse)
  - bloom at neem scope drills down left (inserts at beginning)
  - loop inserts right or left based on scope comparison (principle 2)
  - Panel carries shuttle highlight as (line, start_col, end_col) segments
- **hexes** — curses TUI with evdev keyboard input
  - evdev reads directly from /dev/input (works on Wayland)
  - auto-detects keyboard device (filters out mice by checking EV_LED)
  - chord indicator and glyph history in debug bar
  - shuttle cursor displayed as inverse video at current scope
  - `just run` opens the TUI, cant-quit (enter+Q) or ctrl-c to exit

## what we just did

- continued splice wheel design (design/splice-wheel.md)
  - read_verse() → read_screed(address) for selective tree traversal
  - clarified suggestions vs authorship: cant-suggest is for tooling
    (type checkers, word completion), not inter-author communication
  - unified bend concept: bends are bends at any scale, shuttle bends
    are fine-grained (10 bits), splice bends are compound (variable length)
  - phase 3 planning: collaborative pentabased corpus
- refined document hierarchy (design/tape-documents.md, spec/tape.md)
  - tapestry as flexible root: links metadata + single root branch at
    any level (verse through opus)
  - documents grow by inserting parent levels (append-only, screeds untouched)
  - banner clarified as a meta loop attachable to any node (tapestry thru verse)
  - strict branch ordering: opus → canto → fit → verse
- cross-pollinated spec and design docs
  - spec/tape.md: shuttle scope, three principles, flexible root, banner as meta
  - spec/input.md: swerve axes, mode sub-kinds, splice wheel section,
    encoding examples, unified bend concept
  - spec/vision.md: shuttle-wheel vs splice-wheel distinction
  - design/tape-documents.md: full hierarchy with canto/opus/meta loops
- worked out pentabased phoneme encoding examples
  - "thanks" → 2ey?kc (Seattle dialect), NG (`?`) as distinct phoneme
  - encoding examples in both spec/input.md and design/splice-wheel.md
- phase 1 merged to main, ready for phase 2

## phase 2: thin client (2026-04-11)

charkha is now a thin client connecting to tiraz over WebTransport

### what changed

- **hexes.py refactored to async** — evdev uses async_read_loop,
  main loop is asyncio-based, curses drain handles terminal input
  and resize
- **wire.py added** — petal-native wire protocol: encode bends as
  2-byte datagrams, decode display glyph streams from tiraz
- **petal.py extended** — added count_value, count_glyph, encode_int,
  decode_int for counted integer encoding (independent implementation,
  same schema as tiraz)
- **PocketLoom no longer used** — document state lives in tiraz,
  charkha is purely wheel + display
- **pywebtransport dependency added**

### what works

- connect to tiraz at localhost:4433/wheel
- type petal glyphs, see rendered verse with shuttle cursor
- space for new neem, space+p for new phrase
- swerve navigation (right-shift + WASD)
- yank delete (left-shift alone)
- enter+Q to quit
- terminal resize handling
- tab switching without losing state

### what's next

- **time axis** — undo/redo via swerve keys (needs skein tree
  walking in tiraz loom)
- **submit verse** — loop-verse to submit and start a new verse
  in the chat stream
- **phoneme reference** — overlay or cheatsheet for glyph mapping
- **scratch buffer** — phase 2 yank with scoop/paste

## open questions

- scratch buffer design — how should scoop/paste interact with
  shuttle scope?
- encoding conventions for edge cases: unstressed vowel reduction,
  geminate consonants, borrowed words, proper nouns
