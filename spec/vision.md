# vision

## the plaza as public square

most document storage systems evoke a vault or a filing cabinet - a secure private place where documents are locked away and access is controlled by an owner

the plaza is the opposite: a public square where documents and fragments of documents are stored in open view for all to see

the name is intentional - a plaza is a place where people gather, where works are displayed on walls as murals, where strangers can sit together and read

## four components

the full system has four distinct roles:

```
┌────────┐  bends    ┌──────┐  panels   ┌─────────┐
│ wheel  │ ────────► │      │ ────────► │ display │
└────────┘           │ loom │           └─────────┘
                     │      │  screeds  ┌────────┐
                     └──────┘ ◄───────► │ plaza  │
                                        └────────┘
```

- **wheel** - an input device belonging to a single participant; streams bends to the loom
- **loom** - the collaborative heart of the system; accepts threads from many wheels, weaves them into documents, renders panels for displays
- **plaza** - a public append-only content-addressed store; persists screeds; can be shared across many looms
- **display** - shows rendered panels to participants; knows nothing about documents

these four roles can be bundled or separated in different ways depending on context:
- for local development: 7oom bundles loom + plaza; sp5n bundles wheel + display
- for a public installation: wheels are handheld devices; the loom runs on a server; the plaza is shared infrastructure; the display is a large shared screen
- for archival: a plaza can outlive any particular loom and its screeds can be re-woven by future looms

## two kinds of display

there are two distinct display contexts in the long-term vision:

**working display** - shows what is currently happening in a loom: the document being collaboratively edited, the active input streams of each participant, the in-progress screeds being woven

**gallery display** - shows finished works from the plaza as objects of appreciation: tapestries displayed as murals on the walls of the plaza, available for anyone passing through to read

the gallery display is the natural expression of the plaza-as-public-square idea - documents are not locked away after authoring but displayed openly as part of a shared cultural space

## participants

a core goal of the system is to put all participants on equal footing regardless of their nature

the loom is designed to accept input threads from:
- humans typing on keyboard wheels
- humans gesturing on touch or motion wheels
- computational agents mapping output tokens to bends
- in the longer term: other kinds of persons (cetaceans, corvids, canines) via wheels designed for their particular modes of expression

the working display shows all active input streams side by side with no stream privileged over another

## documents as public infrastructure

in the current dominant model a document belongs to a person or an organization and others are granted access

in the pentabased model a screed belongs to no one once it is written to a plaza - it is content-addressed, append-only, and freely shareable across looms

this makes documents feel less like property and more like utterances - things said in a public square that can be heard and responded to by anyone present
