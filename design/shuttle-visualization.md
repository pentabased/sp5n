# shuttle cursor visualization

## context

the shuttle cursor tracks position within a verse but there's no visual
feedback in the TUI. without seeing what scope the shuttle is at, yank
and swerve behaviors are confusing. this is the foundation for making
all editing operations feel intuitive.

the shuttle is currently `(phrase_idx, neem_idx)` — always implicitly at
neem scope. blooming appends petals to the current neem. we need to show
which neem is "active" in the rendered output.

## approach: shuttle metadata in Panel

the loom knows where the shuttle is in the document AND how the document
maps to rendered lines. so the loom should compute the shuttle's visual
position during `render()` and include it in the Panel. hexes then just
applies inverse video at the indicated positions.

this keeps the clean separation: the loom owns document + rendering
logic, the display just paints what it's told.

## Panel changes

add a `shuttle` field to Panel — a tuple of `(line, start_col, end_col)`
segments. usually one segment; two if a neem wraps across a line break.

```python
@dataclass(frozen=True)
class Panel:
    width: int
    height: int
    lines: tuple[str, ...]
    shuttle: tuple[tuple[int, int, int], ...]
```

for an empty neem, `start_col == end_col` (zero-width). hexes shows
this as a single inverse-video space to indicate "cursor here".

## render() changes

during rendering, track:
1. which output line each phrase starts on
2. within the shuttle phrase, which column the shuttle neem starts at
3. account for line wrapping

algorithm for finding the neem column within a rendered phrase:
iterate through neems in the phrase, accumulating column offsets
(neem length + 1 for each space separator). skip empty neems (they're
filtered in render_phrase). when we reach the shuttle neem_idx, record
its start and end columns.

then map those phrase-relative columns through wrapping:
- `output_line = phrase_start_line + (col // panel_width)`
- `col_in_line = col % panel_width`

if the neem spans a wrap boundary, emit two segments.

add a helper `_compute_shuttle(phrase_start_lines)` to keep render()
clean. render() tracks `phrase_start_lines` as it builds output lines.

## hexes changes

update `_draw_verse` to accept shuttle segments and apply inverse video
(`curses.A_REVERSE`). curses color support is already initialized
(`curses.init_pair(1, ...)`) but unused — we use the simpler
`A_REVERSE` attribute instead.

draw all text normally, then overdraw the shuttle region(s) with
the reverse attribute. for zero-width shuttles (empty neem), draw
a single inverse-video space.

## worked example

verse with two neems "he770" and "w476", shuttle on "w476":

```
rendered phrase: "he770 w476"
                  01234567890
shuttle neem col:       6..10

panel output line 0: "he770 w476"
shuttle: [(0, 6, 10)]

hexes draws: he770 [w476]    (inverse video on w476)
```

verse with one long neem "he770w476" at panel_width=5, shuttle on it:

```
rendered phrase: "he770w476"
panel output:
  line 0: "he770"
  line 1: "w476"
shuttle wraps: [(0, 0, 5), (1, 0, 4)]

hexes draws: [he770]    (both lines inverse)
             [w476]
```
