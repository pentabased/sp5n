# design notes

informal design records for charkha, loosely following the
context / decision / consequences pattern

these capture the reasoning behind architectural choices so we can
look back on why things are the way they are

## index

- [implementation plan](implementation-plan.md) - phase 1-3 roadmap and module design
- [tape documents](tape-documents.md) - document hierarchy, screeds, and shuttle cursor
- [shuttle visualization](shuttle-visualization.md) - shuttle cursor display in the hexes TUI
- [shuttle scope](shuttle-scope.md) - scope tracking for the shuttle cursor (petal/neem/phrase/verse)
- [splice wheel](splice-wheel.md) - splice wheel interface for position-addressed document operations
- [pynput input](pynput-input.md) - replacing curses keyboard input with pynput for proper chord detection
