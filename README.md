# sp5n

a cli tool for streaming pentabased input from a keyboard

## document scheme

pentabased is a scheme for encoding documents

information in pentabased documents is encoded in petal glyphs stored as 5-bit binary numbers

pentabased features 32 (2**5) petal glyphs that map to a subset of the utf-8 character set

each document is a mosaic describing a tree of screeds

each screed is a content-addressed atomic subtree of an abstact syntax tree encoded as a series of petal glyphs combined with a dynamic mapping of links to other screeds separately encoded as a series of petal glyphs

each screed is composed of a warp and weft

in each screed the weft contains a sequence of petal glyphs that describe an abstract syntax tree with abstract links to other screeds

each weft contains a flat list of the screeds to link to within the corresponding weft

the links between these screeds describe a course tree structure spanning the fine-grained tree structure of the abstract syntax tree described by the glyphs within each screed

mosaic documents are stored within a plaza key value blob store

each weft is stored as a content-addressed blob within the plaza and hash collisions are avoided by appending a reserved no-op glyph to the beginning of a weft that collides with another weft already present in the plaza store

each warp is stored under a unique identifier using a monotonically increasing distributed id scheme within the plaza

a plaze blob store is append-only and warps and wefts can be freely shared between mosaic documents

within each weft petal glyphs describe a abstract syntax tree of loop document nodes

each mosaic has a single root loop node that is the entry point to a single document from the wider plaza document indexing and discovery system

branch loop nodes describe document structure

stem loop nodes then contain blooms of petal glyphs that describe semantic values

### text document scheme

pentabased provides different schemes for encoding different kinds of documents as abstract syntax trees of glyphs across a tree of screeds

tapes (short for tapestry) are a pentabased document scheme for representing narrative text

in the tape scheme documents are displayed within a loom where the stem screeds of the document tree are displayed as a series of panels rendered as text

branch screeds in the tape scheme provide the structure to describe and enumerate the stem screeds

stem screeds each contain blooms of petal glyphs that describe content to be rendered to panels

in the tape scheme loop nodes are not recursive and there are instead a series of branch nodes that hold subdocuments of increasing size

this lack of recursion implies a finite limit to the size of a single tape document which is considered to be a positive feature of the scheme

this scheme provides several classes of abstract syntax tree loop nodes that can appear within screeds:

_bloom_

a bloom is the leaf node of a mosaic document tree that contains a series of from 1 to 32 petal glyphs

each kind of bloom implies a semantic interpretation of its petal glyphs

a neem is the core bloom loop of a tape document

each neem contains a series of petal glyphs that evoke a single semantic token such as a word

other kinds of blooms in a tape document can describe semantic ideas such as quantity or magnitude or enumeration

each bloom loop is described in the same screed as its parent stem loop

_stem_

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

_branch_

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

_meta_

a meta loop is similar to a branch loop except that while each scale of branch loop has a specific loop parent and specific loop or stem children a meta loop can be a child of any root or branch loop (but not a meta loop) and can contain from one or more of a single kind of stem loop

meta loops allow metadata to be attached to root and branch loops

each meta loop occupies its own screed together with its child stems and their child blooms

meta loops may or may not contain blooms that are rendered to a panel

_root_

a root tape loop is always the first loop in the first screed in a tape mosaic document

a tape loop can contain a series of meta loops that contain metadata about the document title, authorship, themes and goals

a tape loop can hold a single child branch loop that then contains either further child branch loops or in the case of a verse directly holds stem loops

a tape loop occupies an entire screed unto itself and links to separate screeds where any meta loops and its opening document branch loop are described


## input scheme

a primary goal of the pentabased document scheme is to foster horizontal collaborative writing groups composed of humans and agents and other persons interested in expressing themselves in text

pentabased documents are generated by a loom that accepts thread input streams from one or more wheel input devices in parallel

sp5n is an instantiation of a pentabased wheel that presents a cli that accepts keyboard input and streams a thread of pentabased input to a loom

in a parallel project we implement a pentabased wheel that directly maps output tokens from a computational agent to a thread input stream

a future goal is to implement pentabased wheels to allow other non-human persons such as cetaceans and corvids and canines to participate as well

## keyboard input

sp5n accepts keyboard input using 32 glyph keys and 4 chord keys

in the default configuration on a qwerty keyboard the 32 glyph keys are mapped to:
- 11 keys of the 'q' row starting with 'q' and moving to the right
- 11 keys of the 'a' row starting with 'a' and moving to the right
- 10 keys of the 'z' row starting with 'z' and moving to the right

and the 4 chord keys are mapped to 'enter' and 'space' and the right and left 'shift' keys

### input model

the sp5n tool shows a view of the current loom in a terminal

this view divides the terminal into a series of streams of panes where each pane maps to a single screed

when a wheel is connected in input mode a loom will display a distinct input stream for that wheel with one or more shuttle input cursors

when multiple wheels are connected to a single loom several parallel input streams may be displayed on the screen at once

keyboard input can manipulate the loom by:

- giving control inputs to manage the state of the system
- manipulating which documents and which parts of documents are visible within the displayed panes
- pulling content from other streams (including the scratch stack and other wheels) into the current input stream
- pushing content from the current stream into a scratch stack
- manipulating the position and number of shuttles within the input stream
- spinning new loops into the document at current shuttle positions
- spinning new petals into the blooms at current shuttle positions

### input modes

these keys are used in a modal input scheme inspired by the vim text editor except that when no chord keys are pressed the system is always in bloom mode which is similar to vim insert mode and other modes can be entered temporarily by holding down a chord key

the pentabased input modes are:

- bloom: {no chord key} spin new petals into the bloom at the current shuttle positions (similar to typing character input in vim insert mode)
- loop: {'space'} spin new loops into parent loops at the current shuttle positions (similar to typing spaces and newlines in vim insert mode)
- yank: {'right-shift'} push and pop nodes between the shuttle and the scratch stack (similar to vim visual / selection mode)
- swerve: {left-shift} manipulate the shuttle position and scope and number (similar to vim normal / navigation mode)
- cant: {'enter'} give commands to manipulate the state of the system (similar to vim command mode)

in the pentabased input scheme a wheel streams a thread composed of a series of bends

each bend encodes a single input combination of a mode (bloom/loop/yank/swerve/cant) and a glyph

if a chord key is pressed and released without also pressing a glyph a single bend is sent with the mode of the pressed chord and the null '-' glyph

holding a chord key while explicitly pressing the null glyph key (default `[{`) sends the same bend as hitting the same chord key by itself

the series of bends encoded in an input thread are interpreted by the loom within the context of the current loom state

for example depending on the number of active shuttles the same bloom bend can insert one or several glyphs (one at each shuttle)

### input serialization

thread input is serialized to a series of glyph pairs where the first glyph maps to one of the five input modes indicated by the current chord key (it is not valid to hold down multiple chord keys at the same time and no chord key pressed indicates bloom mode):

- bloom: {no chord key} '8'
- loop: {'space'} '7'
- yank: {'left-shift'} 'y'
- swerve: {'right-shift'} 'c'
- cant: {'enter'} 'k'

and the second glyph represents either the petal glyph explicitly pressed and released or a null glyph if a chord key was pressed and released without pressing a glyph key

streams of bends are gathered into skeins of 1-32 bends

bends are streamed individually as keys are released but are gathered into skeins by the loom

skeins are referenced by screeds to make the history of a document transparent


## petal scheme

scheme to represent base 32 data using a visually distinct subset of utf-8

```
binary numeric value : utf-8 mapping : default keyboard key : phonetic value
0x00 : - : `[{` : [beat]
0x01 : * : `;:` : [belonging | addressing]
0x02 : 2 : `'"` : TH
0x03 : 3 : `,<` : DH
0x04 : 4 : `.>` : ER
0x05 : ? : `/?` : NG
0x06 : a : `aA` : AE
0x07 : 8 : `bB` : B
0x08 : c : `cC` : S
0x09 : 6 : `dD` : D
0x0a : e : `eE` : EH
0x0b : f : `fF` : F
0x0c : G : `gG` : G
0x0d : h : `hH` : H
0x0e : 5 : `iI` : IH
0x0f : j : `jJ` : JH
0x10 : k : `kK` : K
0x11 : 7 : `lL` : L
0x12 : m : `mM` : M
0x13 : N : `nN` : N
0x14 : 0 : `oO` : OW
0x15 : p : `pP` : P
0x16 : Q : `qQ` : CH
0x17 : r : `rR` : R
0x18 : $ : `sS` : ZH
0x19 : t : `tT` : T
0x1a : µ : `uU` : AH
0x1b : v : `vV` : V
0x1c : w : `wW` : W
0x1d : x : `xX` : SH
0x1e : y : `yY` : Y
0x1f : # : `zZ` : Z
```

### petal phonemes

in the petal scheme there is no distinction between punctuation glyphs and phonetic glyphs as the semantic value given by punctuation in latin text is provided by the structure of the abstract syntax tree

however there are two glyphs that have a meaning in a phonetic context that does not map precisely to a latin phonetic glyph:

- the null glyph 0x00 or '-' describes a pause or beat within a broader phonetic token similar to an em dash or apostrophe
- the relation glyph 0x01 or '*' describes the relationship of belonging to or addressing a person similar to the possesive apostrophe in the text "alice's"

the following 30 glyphs map more or less to the phonemes described by the latin and similar alphabets (shown in the table below)

all consonant phonemes map to a single petal glyph while some vowel phonemes are described by a vowel followed by a modifying 'h', 'w' or 'y' consonant

```
        (beat)             | -
 '      alice's            | *
AA      odd     AA D       | ah
AE      at      AE T       | a
AH      hut     HH AH T    | µ
AO      ought   AO T       | aw
AW      cow     K AW       | 0w
AY      hide    HH AY D    | ay
UH      hood    HH UH D    | µh
UW      two     T UW       | ew
OW      oat     OW T       | 0
OY      toy     T OY       | 0y
EH      Ed      EH D       | e
EY      ate     EY T       | ey
IH      it      IH T       | 5
IY      eat     IY T       | 5y
ER      hurt    HH ER T    | 4
NG      ping    P IH NG    | ?
B       be      B IY       | 8
CH      cheese  CH IY Z    | Q
D       dee     D IY       | 6
DH      thee    DH IY      | 3
F       fee     F IY       | f
G       green   G R IY N   | G
HH      he      HH IY      | h
JH      gee     JH IY      | j
K       key     K IY       | k
L       lee     L IY       | 7
M       me      M IY       | m
N       knee    N IY       | N
P       pee     P IY       | p
R       read    R IY D     | r
S       sea     S IY       | c
SH      she     SH IY      | x
T       tea     T IY       | t
TH      theta   TH EY T AH | 2
V       vee     V IY       | v
W       we      W IY       | w
Y       yield   Y IY L D   | y
Z       zee     Z IY       | #
ZH      seizure S IY ZH ER | $
```
