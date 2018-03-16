Annotation details
==================

Aside from adding ``\sameword{}``-macros as appropriate the script also converts
all combined unicode characters into single point variants where they are
available. That means that if you compose 006F (o) and 0308 (̈) they will be
converted into the single code point 00F6 (ö). This ensures matching in these
ambiguous cases if the two systems should be mixed. On this, see `here
<https://en.wikipedia.org/wiki/Unicode_equivalence>`_
