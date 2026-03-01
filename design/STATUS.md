# sp5n status

last updated: 2026-02-28 (session 2)

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

- designed the agent/token wheel interface (design/agent-wheel.md)
  - keyboard wheel vs token wheel: about input granularity, not who's using it
  - token wheel API: position-addressed insert/replace/delete at neem/phrase level
  - read_screed(address) for selective document tree traversal
  - multi-author editing panes: authors are peers, yank between panes
  - suggestions vs authorship: cant-suggest is for tooling, not inter-author
  - phasing: phase 2 token wheel impl, phase 3 initial corpus
- worked out pentabased phoneme encoding examples
  - "hello world" → he770 w476, "thanks for all the fish" → 2a?kc f4 aw7 3µ f5x
  - identified NG (`?`) as a tricky phoneme to internalize
  - dialectal variation is welcome (e.g. ah7 vs aw7 for "all")
- cross-pollinated spec and design docs
  - spec/tape.md: added shuttle scope levels and three principles
  - spec/input.md: added swerve axes, mode sub-kinds, token wheel section,
    encoding examples, fixed yank/swerve chord key assignments
  - spec/vision.md: added keyboard-wheel vs token-wheel distinction
  - design/tape-documents.md: added canto/opus hierarchy and meta loops from spec

## what's next

- **phase 2: 7oom extraction** — extract loom and plaza into a separate
  service, connect sp5n as a thin client
- **time axis implementation** — swerve undo/redo keys mapped but edit
  history tree not yet built in the loom (better over proper screed tree)
- **token wheel implementation** — position-addressed API for agents
- **phoneme reference** — overlay or cheatsheet for glyph-to-phoneme mapping
- **phase 2 yank** — scratch buffer for copy/cut/paste operations
- **phase 3: initial corpus** — collaborative pentabased document corpus

## open questions

- scratch buffer design for phase 2 yank — how should scoop/paste
  interact with the shuttle scope?
- encoding conventions for edge cases: unstressed vowel reduction,
  geminate consonants, borrowed words, proper nouns
