# tape documents

> "i asked a screed what it wants to be and it told me a song"

## screeds

a **screed** is the atomic unit of a pentabased document. each screed
holds a single card of content, evoking the hypercard tradition of
small, self-contained document units.

for tape documents, a screed holds a single verse (or a banner).

## document hierarchy

```
Tapestry (root)
└── Fit (a story/chapter)
    ├── Banner screed (optional title/summary)
    ├── Verse screed
    │   ├── Phrase
    │   │   ├── Neem ("hello")
    │   │   └── Neem ("world")
    │   └── Phrase
    │       └── Neem ...
    ├── Verse screed
    │   └── ...
    └── ...
```

node types bottom-up:
- **Neem** - a sequence of petals evoking a single word
- **Phrase** - a sequence of neems evoking a thought
- **Verse** - a sequence of phrases developing a theme (one screed)
- **Banner** - a title or summary phrase (one screed)
- **Fit** - a series of screeds developing a narrative
- **Tapestry** - the root, a collection of fits

the `-` (beat) glyph within a neem acts as a compound-word separator,
joining multiple words into a single token (like `he770-w476` for
"hello-world").

## shuttle

the **shuttle** is a cursor within a screed, evoking the action of
weaving thread onto a loom. it has a **position** and a **scope**.

the shuttle's maximum scope is one screed (one verse for tape
documents). navigation between screeds is a separate mechanism.

### scope levels (within a verse)

- **petal** - a single petal within a neem
- **neem** - a whole word
- **phrase** - a whole line/thought
- **verse** - the entire screed (max scope)

### visual notation

- `[...]` = shuttle highlighting a node (neem, phrase, or verse scope)
- `|` = shuttle at petal scope (cursor between/after petals)
- empty scope shown as `[  ]`

### three principles

1. **on insert, the shuttle takes the scope of the insert** — insert a
   petal and the shuttle is at petal scope on that petal. insert a new
   neem and the shuttle is at neem scope on the new neem. insert a new
   phrase and the shuttle is at phrase scope on the new phrase.

2. **insert direction depends on scope** — when inserting something
   at the same level or bigger than the current shuttle scope, it goes
   to the **right** (after). when inserting something smaller than the
   current shuttle scope, it goes to the **left** (beginning).

3. **only yank can remove or replace content** — bloom and loop only
   ever create new content. there is no implicit overwriting.

### bloom behavior

bloom always drills down to petal insertion, auto-scaffolding any
intermediate loops needed to hold a petal at the current position.

after inserting a petal, the shuttle is always at petal scope on the
newly inserted petal (by principle 1). subsequent blooms insert to the
right (by principle 2, since petal = petal scope).

**typing into an empty verse:**
```
start:       empty verse, shuttle at verse scope [         ]
bloom h:     drill down left → scaffold phrase/neem,
             insert h, shuttle → petal scope: h|
bloom e:     petal scope, insert right: he|
bloom 7:     he7|
bloom 7:     he77|
bloom 0:     he770|
```

**bloom at neem scope (navigated to an existing neem):**
```
state:       he770 [w476]    shuttle at neem scope
bloom t:     drill down left into neem → insert t at beginning,
             shuttle → petal scope: he770 t|w476
```

**bloom at phrase scope:**
```
state:       [he770 w476]    shuttle at phrase scope
             t 8µN
bloom r:     drill down left → new neem at beginning of phrase,
             insert r, shuttle → petal scope:
             r| he770 w476
             t 8µN
```

### loop behavior

loop inserts a new empty node of the specified type. the shuttle
takes the scope of the new node (by principle 1).

**loop-neem while typing (neem > petal → right):**
```
state:       he770|          shuttle at petal scope
loop-neem:   new neem after current neem,
             shuttle → neem scope: he770 [  ]
bloom w:     drill down left into empty neem, insert w,
             shuttle → petal scope: he770 w|
```

**loop-phrase while typing (phrase > petal → right):**
```
state:       he770 w|        shuttle at petal scope
loop-phrase: new phrase after current phrase,
             shuttle → phrase scope:
             he770 w
             [               ]
bloom t:     drill down left → scaffold neem, insert t:
             he770 w
             t|
```

**loop-neem at phrase scope (neem < phrase → left):**
```
state:       [he770 w476]    shuttle at phrase scope
loop-neem:   new neem at beginning of phrase,
             shuttle → neem scope: [  ] he770 w476
bloom t:     drill down, insert t:
             t| he770 w476
```

**loop-phrase at verse scope (phrase < verse → left):**
```
state:       [he770 w476]    shuttle at verse scope
             [t 8µN     ]
loop-phrase: new phrase at beginning of verse,
             shuttle → phrase scope:
             [               ]
             he770 w476
             t 8µN
bloom N:     drill down left → scaffold neem, insert N:
             N|
             he770 w476
             t 8µN
```

### swerve behavior

swerve moves or rescopes the shuttle without modifying content. there
are four axes of movement, mapped to a WASD-like layout on the left
hand (shown here as physical keys → petal glyphs):

```
  Q   W   E         scoop  grow  stretch      selection / scope
  A   S   D         back   shrink forward      tree
  Z   X   C         undo   redo-L redo-R       time
```

#### scope axis (W/S → grow/shrink)

- **grow** (`w`) - expand shuttle scope to the parent node
- **shrink** (`$`) - reduce shuttle scope to the last child. at petal
  scope on a petal within a neem, shrink is a no-op.

when shrinking into a node, the shuttle goes to the **last** (rightmost)
child — this puts you at the natural "append" position for continued
typing. when growing, the shuttle expands to cover the parent of the
current scope.

#### tree axis (A/D → back/forward)

- **back** (`a`) - move shuttle to previous sibling at the current
  scope level
- **forward** (`6`) - move shuttle to next sibling at the current
  scope level

#### time axis (Z/X/C → undo/redo)

- **undo** (`#`) - step backward in edit history
- **redo-left** (`x`) - step forward in edit history, taking the left
  branch at a fork
- **redo-right** (`c`) - step forward in edit history, taking the right
  branch at a fork

edit history is a **binary tree**, not a linear undo stack. when you
undo and then make a new edit, you create a fork. navigating forward
requires choosing left or right at each fork. when there is only one
path forward, either redo key works.

any number of divergent edits from the same point can be modeled as a
series of binary splits:

```
instead of:       you get:
    A                 A
   /|\               / \
  B C D             B   *
                       / \
                      C   D
```

two keys are always enough — binary splits can encode any number of
choices, you just take a few extra steps to reach deeper branches.

#### selection axis (Q/E → scoop/stretch)

- **scoop** (`Q`) - expand shuttle selection one child to the left
- **stretch** (`e`) - expand shuttle selection one child to the right

selection allows the shuttle to serve as both cursor and selection by
growing one child at a time in either direction. (phase 2)

### cant behavior

the null cant (enter alone, `-`) is reserved for **accepting
suggestions** from the loom — e.g. autocomplete predictions,
completions offered by an attached language model.

undo is handled by **swerve-undo** (`#`, Z key) on the time axis.
deletion is handled by **yank-delete** (`#`, Z key in yank mode).
