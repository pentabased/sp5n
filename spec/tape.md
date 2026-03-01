# tape document scheme

pentabased provides different schemes for encoding different kinds of documents as abstract syntax trees of glyphs across a tree of screeds

tapes (short for tapestry) are a pentabased document scheme for representing narrative text

in the tape scheme documents are displayed within a loom where the stem screeds of the document tree are displayed as a series of panels rendered as text

branch screeds in the tape scheme provide the structure to describe and enumerate the stem screeds

stem screeds each contain blooms of petal glyphs that describe content to be rendered to panels

in the tape scheme loop nodes are not recursive and there are instead a series of branch nodes that hold subdocuments of increasing size

this lack of recursion implies a finite limit to the size of a single tape document which is considered to be a positive feature of the scheme

this scheme provides several classes of abstract syntax tree loop nodes that can appear within screeds:

## bloom

a bloom is the leaf node of a mosaic document tree that contains a series of from 1 to 32 petal glyphs

each kind of bloom implies a semantic interpretation of its petal glyphs

a neem is the core bloom loop of a tape document

each neem contains a series of petal glyphs that evoke a single semantic token such as a word

other kinds of blooms in a tape document can describe semantic ideas such as quantity or magnitude or enumeration

each bloom loop is described in the same screed as its parent stem loop

## stem

stem loops do not occupy their own screed but are described within the screed containing their parent loop (either a verse or meta loop)

stem loops are not recursive but can contain either smaller stem loops or blooms of glyphs

each kind of stem presents implications for how to interpret the semantic content of its bloom children

the core stem loops of the tape scheme are phrases

a phrase contains a series of neems evoking a thought

a phrase loop can be the child of either a verse loop or one of the meta stem loops

other kinds of stem loops describe other semantic concepts such as:
- a handle for a person
- a reference to another mosaic document
- a key / value pair
- a note commenting on a section of text
- a banner introducing the contents of the following branch loop
- a title describing the scope and goals of a tape document

## branch

as tape loops are not recursive the scheme offers several levels of branch loop that can each contain an increasingly large subdocument

each branch loop occupies its own screed where it lists a series of child loops

if these child loops are also branches they are given as a link to another screed

if these child loops are stems they are described directly within the current screed

the smallest branch loop is a verse which contains a series of phrases developing a theme

the rest of the branch loops in increasing order of size are:
- fit: a series of verses tracing a narrative arc
- canto: a series of fits portraying a slice of the world
- opus: a series of cantos providing a comprehensive view of a system within the world

the branch levels form a strict ordering where each level can only contain children of the next level down: opus → canto → fit → verse

these branch loop names are taken from the tradition of epic poetry and describe subdocuments of increasing size with an opus (containing a series of cantos) being the largest kind of text document that can be described within the tape scheme

## meta

a meta loop can be a child of any node from the tapestry root through a verse (but not of another meta loop) and can contain one or more of a single kind of stem loop

meta loops allow metadata to be attached to root and branch loops

each meta loop occupies its own screed together with its child stems and their child blooms

meta loops may or may not contain blooms that are rendered to a panel

a banner is an example of a meta loop — a title or summary phrase that introduces the node it is attached to — a tapestry can have a banner for its document title and a fit can have a banner for its chapter title and a verse can have a banner for a section heading

## root

a tapestry is the root loop of a tape document and the entry point for indexing and discovery in the plaza

a tapestry occupies an entire screed unto itself and links to separate screeds where its meta loops and its root branch loop are described

a tapestry can contain a series of meta loops that contain metadata about the document title, authorship, themes and goals

a tapestry links a single root branch loop at any level of the branch hierarchy — a document can be as small as a single verse or as large as a full opus

different documents naturally want to be different sizes so the root branch level is flexible:

- tapestry → verse (a quick thought)
- tapestry → fit → verses (a short narrative)
- tapestry → canto → fits → verses (a longer work)
- tapestry → opus → cantos → fits → verses (a comprehensive work)

documents grow by inserting parent levels — when a tapestry → verse needs more verses a new fit is created containing the existing verse plus new ones and the tapestry now points to the fit — the original verse screed is untouched in the plaza

## shuttle

the shuttle is a cursor within a screed, evoking the action of weaving thread onto a loom

a shuttle has a position and a scope

the shuttle's maximum scope is one screed (one verse for tape documents) and navigation between screeds is a separate mechanism

### scope levels

within a verse the shuttle has four scope levels:

- **petal** - a single petal within a neem
- **neem** - a whole word
- **phrase** - a whole thought
- **verse** - the entire screed

### three principles

the shuttle's behavior follows three principles:

1. **on insert the shuttle takes the scope of the insert** — insert a petal and the shuttle is at petal scope on that petal; insert a new neem and the shuttle is at neem scope on the new neem; insert a new phrase and the shuttle is at phrase scope on the new phrase

2. **insert direction depends on scope** — when inserting something at the same level or bigger than the current shuttle scope it goes to the right (after); when inserting something smaller than the current shuttle scope it goes to the left (beginning)

3. **only yank can remove or replace content** — bloom and loop only ever create new content; there is no implicit overwriting
