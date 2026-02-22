# sp5n

a keyboard input and display tool for collaborative tapestry authoring

## what is this?

a loom is a collaborative writing environment where several authors - human and AI alike - each spin an input thread on a wheel and the threads are woven together into a shared tapestry

sp5n is a keyboard wheel for the loom - a terminal tool that maps keyboard input to a pentabased thread and streams it to a loom server, while also displaying the rendered tapestry and the input streams of other participants

tapestries are narrative text documents encoded in pentabased, a minimal document scheme that combines a 32-glyph character encoding with a structured document format into a single compact representation

the companion server for local development is [7oom](7oom/README.md), which bundles a plaza document store and a loom together into a single containerized service

## motivation

most collaborative writing tools treat one person as the owner of a document and others as guests

in a loom all participants - including computational agents - have equal standing

each author works in their own input stream, visible to the group, and screeds (card-sized subtrees of the document) can be woven into the shared tapestry by group agreement

the underlying pentabased encoding is designed to support this model: documents are not large flat files but trees of small content-addressed screeds that can be shared, reused, and collaboratively assembled across a plaza document store

## architecture

```
  ┌─────────┐   thread   ┌───────────────────┐
  │  sp5n   │ ─────────► │      7oom         │
  │         │            │                   │
  │ keyboard│ ◄───────── │  plaza  +  loom   │
  │ display │   changes  │                   │
  └─────────┘            └───────────────────┘
```

the general terms for the components of this system are:

- **wheel** - an input device that streams a thread of pentabased bends to a loom
- **loom** - a server that accepts input threads and maintains the shared document state
- **plaza** - an append-only content-addressed store where screeds are persisted
- **thread** - a stream of input bends from a single wheel
- **screed** - a card-sized atomic subtree of a tapestry document
- **tapestry** - a narrative text document composed of a tree of screeds

sp5n provides both wheel input and loom display in a single terminal interface

7oom provides both plaza storage and loom logic in a single local server

## getting started

**prerequisites:** python 3.13+, [just](https://github.com/casey/just)

```sh
git clone https://github.com/pentabased/sp5n
cd sp5n
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

see [sp5n/README.md](sp5n/README.md) for the current implementation plan

## docs

- [spec/](spec/README.md) - pentabased encoding and document scheme
- [7oom/](7oom/README.md) - minimal plaza and loom server for local development
- [sp5n/](sp5n/README.md) - implementation plan for this package
