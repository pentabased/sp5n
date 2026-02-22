# pentabased encoding

## document scheme

pentabased is a scheme for encoding documents

information in pentabased documents is encoded in petal glyphs stored as 5-bit binary numbers

pentabased features 32 (2**5) petal glyphs that map to a subset of the utf-8 character set

each document is a mosaic composed of a fine-grained abstract syntax tree spread across a course-grained tree of screed subdocuments

each screed is a content-addressed atomic subtree of the overall abstact syntax tree encoded as a series of petal glyphs combined with a dynamic mapping of links to other screeds separately encoded as a series of petal glyphs

these two parts of a screed are the a warp and weft

in each screed the weft contains a sequence of petal glyphs that describe an abstract syntax tree with abstract links to other screeds

each weft contains a flat list of the screeds to link to within the corresponding weft

the links between these screeds describe a course tree structure spanning the fine-grained tree structure of the abstract syntax tree described by the glyphs within each screed

mosaic documents are stored within a plaza key value blob store

each weft is stored as a content-addressed blob within the plaza and hash collisions are avoided by appending a reserved no-op glyph to the beginning of a weft that collides with another weft already present in the plaza store

each warp is stored under a unique identifier using a monotonically increasing distributed id scheme within the plaza

a plaza blob store is append-only and warps and wefts can be freely shared between mosaic documents

within each weft petal glyphs describe a abstract syntax tree of loop document nodes

each mosaic has a single root loop node that is the entry point to a single document from the wider plaza document indexing and discovery system

branch loop nodes describe document structure

stem loop nodes then contain blooms of petal glyphs that describe semantic values
