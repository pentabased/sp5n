# agent wheel

## context

the keyboard wheel translates physical key events into bends — one
petal at a time, with a shuttle cursor that tracks position and scope.
this interaction model is shaped by the constraints of real-time
keyboard input: the operator can only press one key at a time, needs
to navigate by feel, and builds up content incrementally.

a token-based input source has different constraints. it produces
output in chunks (words, phrases), can reference any position in the
document directly, and naturally operates at neem or phrase granularity
rather than individual petals. emitting 32 separate bloom bends to
write a six-word phrase would be absurdly inefficient.

the loom needs to accept input from both kinds of sources. the
architecture already anticipates this — the four-component model
(wheel → loom ← display, loom ↔ plaza) treats the wheel as a
pluggable input source. we just need a second wheel variant.

## two kinds of wheel

the keyboard wheel and the token wheel are two ways to feed thread
onto the loom. the distinction is about input granularity, not about
who's using it — a human could use a token wheel (e.g. dictation),
and an animal could use a keyboard wheel.

```
keyboard wheel (petals)          token wheel (neems/phrases)
       │                                │
   bloom bends                  insert/replace/delete
   one petal at a time          at neem or phrase granularity
       │                                │
       └──────────► loom ◄──────────────┘
                     │
                     ▼
                   panel
```

the keyboard wheel's atomic unit is a single bloom bend. the shuttle
cursor is essential — it tells the operator where they are and what
scope they're operating at.

the token wheel's atomic units are neems and phrases. the shuttle is
not useful — the operator can specify exactly where to act by
addressing positions in the document tree directly.

## token wheel API

the token wheel operates on the document tree with position-addressed
operations. no shuttle state is maintained — each operation specifies
its target explicitly.

### addressing

positions in the verse tree are addressed as tuples:

```
phrase address:     (phrase_idx,)
neem address:       (phrase_idx, neem_idx)
petal address:      (phrase_idx, neem_idx, petal_idx)
```

### operations

**insert_neem(phrase_idx, neem_idx, petals)**

insert a new neem at the given position within a phrase. existing
neems at and after `neem_idx` shift right. the petals argument is
a sequence of Petal values.

```python
# insert "w476" as second neem in first phrase
loom.insert_neem(0, 1, ["w", "4", "7", "6"])
```

**insert_phrase(phrase_idx, neems)**

insert a new phrase at the given position. existing phrases shift
down. neems is a list of petal sequences.

```python
# insert "2a?kc f4 aw7 3µ f5x" (thanks for all the fish) as second phrase
loom.insert_phrase(1, [
    ["2", "a", "?", "k", "c"],
    ["f", "4"],
    ["a", "w", "7"],
    ["3", "µ"],
    ["f", "5", "x"],
])
```

**replace_neem(phrase_idx, neem_idx, petals)**

replace the contents of an existing neem. the neem keeps its position
in the tree but gets new petals.

**replace_phrase(phrase_idx, neems)**

replace the contents of an existing phrase with new neems.

**delete_neem(phrase_idx, neem_idx)**

remove a neem. if it's the last neem in a phrase, the phrase is
removed too (same semantics as yank-delete at neem scope).

**delete_phrase(phrase_idx)**

remove an entire phrase.

**read_screed(address)**

return the screed at the given address in the document tree. the
screed contains the node's content and metadata about its children,
allowing selective traversal — an operator can read a parent screed
to decide which children are worth descending into, rather than
loading the entire document into context.

```python
# read the root screed to see top-level structure
root = loom.read_screed(())

# read a specific verse to see its phrases
verse = loom.read_screed((verse_idx,))

# read a specific phrase to see its neems
phrase = loom.read_screed((verse_idx, phrase_idx))
```

### why no shuttle?

the shuttle is valuable for keyboard wheels because:
- the operator can only see a screen-sized window of the document
- navigation is physical (chord + key)
- scope changes give tactile feedback about what you're editing

none of these apply to token wheels. a token wheel operator can hold
the entire document in context, address any position directly, and
doesn't benefit from incremental scope discovery. a two-argument
`(position, content)` call is more natural than `navigate(); then
edit()`.

each keyboard wheel owns its own shuttle. token wheels have no
shuttle. the loom adjusts keyboard-wheel shuttle indices when any
wheel's operations shift positions around.

## bends

a **bend** is the atomic unit of input on any thread — one
indivisible instruction from a wheel to the loom. the word evokes
a sailor's bend (a useful and stable configuration of a line), a
physical feature on a thread, and the act of skillfully shaping a
medium.

both wheel types produce bends, but at different scales:

- **keyboard bends** are fine-grained: a mode + a glyph (two petals,
  10 bits). a keyboard thread is like embroidery thread — many tiny
  bends per neem.
- **token bends** are compound: an operation + an address + content
  (variable length). a token thread is like yarn — each bend carries
  a neem or phrase worth of material.

the loom doesn't care about bend size. it applies each bend to the
document as an atomic operation. both types of bend mutate the same
verse, and the loom is the arbiter of document state regardless of
input source.

keyboard bends have a compact 10-bit wire format for real-time
streaming. token bends have their own format (a tagged operation
with variable-length payload). in phase 2, when the loom moves to
7oom, these become two API endpoints — different protocols, same
document.

## encoding

the token wheel can work with petals directly (as shown above) or
with a convenience layer that encodes English text to pentabased:

```python
# convenience: encode from English
wheel.write("hello world")
# → inserts neems ["h","e","7","7","0"] and ["w","4","7","6"]

# direct: provide petals
wheel.insert_neem(0, 0, ["h", "e", "7", "7", "0"])
```

the encoding layer maps English phonemes to pentabased glyphs using
the same phonetic scheme defined in the spec. this is a separate
concern from the document operations — the token wheel API always
works with petals at the lowest level.

### encoding examples

pentabased uses 32 glyphs to represent English phonemes. each
consonant maps to a single petal. vowels are either a single petal
(short/simple vowels) or a two-petal digraph (diphthongs and long
vowels, formed by a vowel petal followed by a modifying consonant
h/w/y).

**single-petal vowels**: a (AE, "at"), e (EH, "Ed"), 5 (IH, "it"),
µ (AH, "hut"), 0 (OW, "oat"), 4 (ER, "hurt")

**two-petal vowel digraphs**: ah (AA, "odd"), aw (AO, "ought"),
ay (AY, "hide"), ey (EY, "ate"), 5y (IY, "eat"), 0y (OY, "toy"),
0w (AW, "cow"), ew (UW, "two"), µh (UH, "hood")

worked examples:

```
hello world
  h e 7 7 0    w 4 7 6
  HH EH L L OW   W ER L D
  "he770 w476"

thanks for all the fish
  2 a ? k c    f 4    a w 7    3 µ    f 5 x
  TH AE NG K S   F ER   AO L    DH AH   F IH SH
  "2a?kc f4 aw7 3µ f5x"

the quick brown fox
  3 µ    k w 5 k    8 r 0w N    f ah k c
  DH AH   K W IH K   B R AW N    F AA K S
  "3µ kw5k 8r0wN fahkc"

she sells seashells by the seashore
  x 5y    c e 7 #    c 5y x e 7 #    8 ay    3 µ    c 5y x aw r
  SH IY    S EH L Z    S IY SH EH L Z   B AY    DH AH   S IY SH AO R
  "x5y ce7# c5yxe7# 8ay 3µ c5yxawr"
```

note: pentabased is phonetic, not orthographic. "for" can be encoded
as full `fawr` (F AO R) or reduced `f4` (F ER) depending on how it
sounds in context. the encoding reflects pronunciation, so dialectal
variation is expected and welcome — `ah7` (AA L) for "all" is valid
in dialects with the cot-caught merger.

## multi-author editing

a document can have multiple authors, each with their own wheel
feeding thread onto the loom. the TUI layout reflects this:

```
┌─────────────────┬──────────────────────┐
│                 │  author A (keyboard) │
│  document tree  │  ┌shuttle cursor───┐ │
│                 │  │ 2a?kc f4 aw7    │ │
│  verse 1        │  │ 3µ f5x          │ │
│    phrase 1     │  └─────────────────┘ │
│    phrase 2     ├──────────────────────┤
│  verse 2        │  author B (token)    │
│    phrase 1     │  no shuttle          │
│                 │  position-addressed  │
│                 │  operations          │
└─────────────────┴──────────────────────┘
```

- the document tree is displayed on the left
- each author has their own editing pane on the right
- keyboard-wheel panes show the shuttle cursor
- token-wheel panes have no shuttle visualization
- authors can access each other's editing panes like scratch buffers
  (the phase 2 yank mechanism with scoop/paste)

all authors are peers. if a keyboard-wheel author likes what a
token-wheel author wrote, they yank it — same as copying from any
other author's pane.

### suggestions vs authorship

the cant-suggest mechanism (enter alone = accept suggestion) is for
**tooling**, not for inter-author communication. suggestions come from
language servers running in an editing pane — type checkers, word
completion, spellcheck — things that help a keyboard-wheel operator
type faster by offering the next neem or phrase.

suggestions are not useful for token-wheel operators. a token wheel
can emit a whole phrase at once and has its own judgment about content.
however, tooling that flags **errors** (type mismatches, malformed
neems) is useful as a read-only annotation on the document tree —
information an operator would want before deciding what to edit, but
not a suggest/accept flow.

### index adjustment

when any wheel's operations shift positions in the document tree, the
loom adjusts all keyboard-wheel shuttle indices accordingly. for
example, if a token wheel inserts a phrase above the keyboard wheel's
current position, the keyboard wheel's phrase_idx increments by one.
token wheels need no adjustment since they specify positions explicitly
per operation.

## phasing

### phase 1 (current)

the design work is about ensuring the document model supports both
keyboard and token wheel interaction patterns. the current tape
semantics (verse/phrase/neem/petal) work unchanged — no modifications
needed. the three principles (scope-of-insert, direction-by-scope,
only-yank-removes) apply to keyboard wheels only. token wheels have
their own simpler semantics: direct addressing, explicit operations.

### phase 2: token wheel implementation

the token wheel requires the loom to be extracted into 7oom as a
separate service. keyboard wheels and token wheels become client
connections to the same 7oom instance.

### phase 3: initial corpus

once the document store is reasonably stable, build an initial corpus
of documents rendered in pentabased. this serves several purposes:

- stress-test the encoding scheme against varied real text
- surface edge cases in the phoneme mapping (unstressed vowel
  reduction, geminate consonants, borrowed words, proper nouns)
- establish encoding conventions where the spec leaves room for
  interpretation
- provide reference material for new pentabased learners
- develop fluency for both keyboard-wheel and token-wheel authors

the corpus would be a collaborative effort between keyboard-wheel and
token-wheel authors — a practical test of the multi-author editing
model as well as the encoding scheme itself.
