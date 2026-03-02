# charkha

a shuttle wheel for collaborative tapestry authoring

## what is this?

a loom is a collaborative writing environment where several authors - human and AI alike - each spin an input thread on a wheel and the threads are woven together into a shared tapestry

charkha is a shuttle wheel for the loom - a terminal tool that maps keyboard input to a pentabased thread and streams it to a loom server, while also displaying the rendered tapestry and the input streams of other participants

tapestries are narrative text documents encoded in pentabased, a minimal document scheme that combines a 32-glyph character encoding with a structured document format into a single compact representation

the companion server for local development is [tiraz](https://github.com/pentabased/tiraz), which bundles a plaza document store and a loom together into a single containerized service

## motivation

most collaborative writing tools treat one person as the owner of a document and others as guests

in a loom all participants - including computational agents - have equal standing

each author works in their own input stream, visible to the group, and screeds (card-sized subtrees of the document) can be woven into the shared tapestry by group agreement

the underlying pentabased encoding is designed to support this model: documents are not large flat files but trees of small content-addressed screeds that can be shared, reused, and collaboratively assembled across a plaza document store

## architecture

the system has three general components:

```
  ┌────────┐  bends   ┌──────────────────┐  panels  ┌─────────┐
  │ wheel  │ ───────► │  plaza  +  loom  │ ───────► │ display │
  └────────┘          └──────────────────┘          └─────────┘
```

- **wheel** - streams a thread of input bends from a single author to the loom
- **loom** - accepts input threads, maintains shared document state, renders panels
- **plaza** - append-only content-addressed store where screeds are persisted (part of the loom server)
- **display** - receives rendered panels from the loom and shows them to participants

the loom owns all document logic and rendering - wheels are input-only and displays are output-only, so either can be swapped out independently (a phone as a wheel, a big shared screen as a display)

charkha is a terminal client that plays both the wheel and display roles

tiraz is a local server that plays both the plaza and loom roles

general terms for the data flowing through the system:

- **bend** - a single input event: one mode (bloom/loop/yank/swerve/cant) + one glyph
- **thread** - a stream of bends from a single wheel
- **panel** - a fixed-size block of rendered text produced by the loom
- **screed** - a card-sized atomic subtree of a tapestry document, persisted in the plaza
- **tapestry** - a narrative text document composed of a tree of screeds

## getting started

**prerequisites:** python 3.13+, [just](https://github.com/casey/just)

```sh
git clone https://github.com/pentabased/charkha
cd charkha
just init
```

available commands:

```sh
just          # list available recipes
just repl     # start a python repl in the venv
just format   # autoformat code
just typecheck  # run static type checking
just test     # run unit tests
just validate # run all checks
```

## status

early prototype - the pentabased encoding, tapestry document scheme, and input model are specified but not yet fully implemented

see [design/](design/README.md) for design notes and implementation plan

## docs

- [spec](https://github.com/pentabased/spec) - pentabased encoding and document scheme
- [tiraz](https://github.com/pentabased/tiraz) - minimal plaza and loom server for local development
- [design/](design/README.md) - design notes for this package
