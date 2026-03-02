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

## what's next

- **phase 2: tiraz extraction** — extract loom and plaza into a separate
  service, connect charkha as a thin client
- **time axis implementation** — swerve undo/redo keys mapped but edit
  history tree not yet built in the loom (better over proper screed tree)
- **splice wheel implementation** — position-addressed API for agents
- **phoneme reference** — overlay or cheatsheet for glyph-to-phoneme mapping
- **phase 2 yank** — scratch buffer for copy/cut/paste operations
- **phase 3: initial corpus** — collaborative pentabased document corpus

## open questions

- scratch buffer design for phase 2 yank — how should scoop/paste
  interact with the shuttle scope?
- encoding conventions for edge cases: unstressed vowel reduction,
  geminate consonants, borrowed words, proper nouns
