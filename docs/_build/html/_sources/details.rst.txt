Annotation details
==================

Aside from adding ``\sameword{}``-macros as appropriate the script also converts
all combined unicode characters into single point variants where they are
available. That means that if you compose 006F (o) and 0308 (̈) they will be
converted into the single code point 00F6 (ö). This ensures matching in these
ambiguous cases if the two systems should be mixed. On this, see `here
<https://en.wikipedia.org/wiki/Unicode_equivalence>`_

Languages
=========

The script is fully Unicode 10 compliant and should therefore handle any
language that is represented in unicode characters. Characters that are
considered to be part of a word matches the
`Unicode definition <https://www.unicode.org/reports/tr29/>`_.

It has however not been tested with any languages that are not left-to-right.

If you find any problems with any language, you should
`file a bug report <https://github.com/stenskjaer/samewords/issues>`_.
