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

Overlapping apparatus entries
=============================

In cases where it is necessary to create two apparatus entries that overlap, the
line numbers of the overlapping structure must be indicated manually (the
``\xxref{}`` can assist with that).

.. code-block:: latex

   \beginnumbering
   \pstart
   One %
   \edtext{
       and two
       \edtext{and}{\xxref{start}{end}\lemma{and–and}\Afootnote{overlapping}}\edlabel{start}%
       four
   }{\lemma{and–four}\Afootnote{del.}}
   and\edlabel{end} five.
   \pend
   \endnumbering

Here the two labels ``\edlabel{start}`` and ``\edlabel{end}`` indicate the
extent of the inner overlapping note.
