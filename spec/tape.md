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

these branch loop names are taken from the tradition of epic poetry and describe subdocuments of increasing size with an opus (containing a series of cantos) being the largest kind of text document that can be described within the tape scheme

## meta

a meta loop is similar to a branch loop except that while each scale of branch loop has a specific loop parent and specific loop or stem children a meta loop can be a child of any root or branch loop (but not a meta loop) and can contain from one or more of a single kind of stem loop

meta loops allow metadata to be attached to root and branch loops

each meta loop occupies its own screed together with its child stems and their child blooms

meta loops may or may not contain blooms that are rendered to a panel

## root

a root tape loop is always the first loop in the first screed in a tape mosaic document

a tape loop can contain a series of meta loops that contain metadata about the document title, authorship, themes and goals

a tape loop can hold a single child branch loop that then contains either further child branch loops or in the case of a verse directly holds stem loops

a tape loop occupies an entire screed unto itself and links to separate screeds where any meta loops and its opening document branch loop are described
