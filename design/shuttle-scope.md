# shuttle scope tracking

## context

the shuttle cursor tracks position at neem level only (`_phrase_idx`,
`_neem_idx`) — there is no scope dimension. the design in
tape-documents.md specifies four scope levels (petal, neem, phrase,
verse) with scope-aware behavior for all operations per three principles:

1. on insert, shuttle takes scope of the insert
2. insert direction depends on scope (same/bigger → right, smaller → left)
3. only yank removes content

the user noticed that bloom doesn't leave the shuttle at petal scope
(it highlights the whole neem instead of just the last petal) and that
grow/shrink swerve doesn't work.

## approach

add explicit scope tracking to PocketLoom. add `_petal_idx` and
`_scope` fields. make bloom, loop, swerve, and yank scope-aware per
the three principles. update `_compute_shuttle()` to highlight
differently based on scope level.

initial scope is NEEM (not VERSE) for backward compatibility — the
behavioral difference is negligible since the first bloom drills to
petal scope regardless.

## changes

### ShuttleScope enum and new fields

```python
from enum import StrEnum

class ShuttleScope(StrEnum):
    PETAL = "petal"
    NEEM = "neem"
    PHRASE = "phrase"
    VERSE = "verse"
```

add to PocketLoom:

```python
_petal_idx: int = field(default=0, init=False)
_scope: ShuttleScope = field(default=ShuttleScope.NEEM, init=False)
```

### bloom becomes scope-aware

new `_bloom` method:

- **petal scope**: insert petal to the RIGHT of `_petal_idx`, advance
  `_petal_idx`. scope stays PETAL.

- **neem scope, empty neem**: insert petal, `_petal_idx = 0`,
  scope → PETAL. (same end result as current behavior)

- **neem scope, non-empty neem**: drill down LEFT — insert petal at
  BEGINNING of neem. `_petal_idx = 0`, scope → PETAL.

  NOTE: this changes behavior when the user navigates to an existing
  neem at neem scope and then types — petal goes at the start, not the
  end. this matches the design's "smaller scope inserts LEFT" principle.

- **phrase scope**: drill down LEFT — scaffold new neem at beginning
  of phrase (or use existing empty first neem), insert petal.
  `_neem_idx = 0`, `_petal_idx = 0`, scope → PETAL.

- **verse scope**: drill down to first phrase, then follow phrase-scope
  logic.

### loop becomes scope-aware

loop-neem:
- at petal/neem scope (neem ≥ petal/neem): insert new neem to the
  RIGHT of current neem. scope → NEEM.
- at phrase/verse scope (neem < phrase/verse): insert new neem to the
  LEFT (beginning of current phrase). scope → NEEM.

loop-phrase:
- at petal/neem/phrase scope: insert new phrase to the RIGHT.
  scope → PHRASE, `_neem_idx = 0`.
- at verse scope (phrase < verse): insert new phrase to the LEFT
  (beginning of verse). scope → PHRASE, `_neem_idx = 0`.

### swerve grow/shrink

grow (`w`): expand scope one level up.
- petal → neem → phrase → verse. no-op at verse scope.

shrink (`$`): reduce scope one level down, go to LAST (rightmost) child.
- verse → phrase: `_phrase_idx = len(self.verse) - 1`
- phrase → neem: `_neem_idx = len(self._current_phrase) - 1`
- neem → petal: `_petal_idx = len(self._current_neem) - 1`.
  no-op on empty neem (can't have petal scope with no petals).
- petal: no-op.

### swerve back/forward at different scopes

- **petal**: move to prev/next petal within neem. no-op at boundaries
  (don't cross neem boundary — user must grow first).
- **neem**: current behavior (move between neems, cross phrase boundary).
- **phrase**: move to prev/next phrase. no-op at verse boundaries.
- **verse**: no-op.

### yank-delete at different scopes

- **petal**: remove petal at `_petal_idx`. move to previous petal.
  if last petal in neem → scope goes to NEEM on empty neem.
- **neem**: current behavior (remove neem, adjust position).
- **phrase**: remove entire phrase. move to previous phrase. if last
  phrase, leave empty scaffold, scope → NEEM.
- **verse**: clear entire verse to empty scaffold (`[[[]]]`).
  scope → NEEM, reset indices.

### _compute_shuttle for different scopes

- **petal**: find the petal's column within the rendered phrase
  (`neem_start_col + _petal_idx`). highlight one character at that
  position, mapped through wrapping.

- **neem**: current behavior — highlight entire neem.

- **phrase**: highlight the entire rendered phrase across all lines
  it spans.

- **verse**: highlight all non-empty content lines.

## verification

- `just validate` passes (all tests green)
- `just run` — after typing, shuttle highlights just the last petal
  (not the whole neem). swerve-grow (right-shift + W) expands to
  neem scope (whole neem highlighted). swerve-shrink (right-shift + S)
  goes back to petal scope. back/forward at petal scope moves the
  highlight character by character.
