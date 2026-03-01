# design notes

informal design records for sp5n, loosely following the
context / decision / consequences pattern

these capture the reasoning behind architectural choices so we can
look back on why things are the way they are

## index

- [implementation plan](implementation-plan.md) - phase 1-3 roadmap and module design
- [tape documents](tape-documents.md) - document hierarchy, screeds, and shuttle cursor
- [shuttle visualization](shuttle-visualization.md) - shuttle cursor display in the hexes TUI
- [shuttle scope](shuttle-scope.md) - scope tracking for the shuttle cursor (petal/neem/phrase/verse)
- [agent wheel](agent-wheel.md) - agent-facing wheel interface for AI interaction with pentabased documents
- [pynput input](pynput-input.md) - replacing curses keyboard input with pynput for proper chord detection
