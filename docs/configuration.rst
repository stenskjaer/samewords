Configuration
~~~~~~~~~~~~~

You can configure a small range of settings relevant for the processing.
This is done in a JSON-formatted file.

You give the location of the config file in the argument ``--config-file``. The
script will automatically look for a config file with the name
``~/.samewords.json``, so if you put it there, you won’t have to specify the
command line argument every time you call the script. That can be very handy if
you often need to use the same configuration.

The configuration file recognizes the following parameters:

- ``exclude_macros``
- ``ellipsis_patterns``
- ``sensitive_context_match``
- ``context_distance``
- ``punctuation``
- ``multiword``

JSON requires backslashes to be escaped if you want to preserved them in
the string. You do that with another backslash, so ``\\`` will result in
a single backslash. You must remember this when noting ``TeX`` strings
or regular expressions that contain backslashes.

An example configuration file can be found in the root directory of the
*Samewords* package or `in the online Github repository
<https://github.com/stenskjaer/samewords/blob/master/sample_config.json>`__.

Example file
------------

An example configuration file could contain the following content:

.. code:: json

    {
      "ellipsis_patterns": [
        "--",
        "–"
      ],
      "exclude_macros": [
        "\\excludedMacro"
      ]
    }



Parameters
----------

``exclude_macros``
^^^^^^^^^^^^^^^^^^

You might want to define some macros which are entirely ignored in the
comparison of text segments. That will typically be macros that *do not*
contain text content.

For example, you might use a custom macro called ``\msbreak{}`` to
indicate a pagebreak in your edition. The content of that is not printed
in the text, but in the margin. So you don’t want the comparison to
figure in the content of this macro. Take this example phrase:

.. code:: latex

    I\msbreak{23v} know that \edtext{I know}{\Afootnote{I don't know B}}
    nothing.

Since the content of (almost) all macros is included by default, this
would give the comparison of the phrase ``I know`` (``\edtext`` content)
with ``I23v know that`` (context). It will not match, and hence not
annotate the phrase.

If we add the macro to the ``excluded_macros`` field in a settings file
and pass that to the script, ``\msbreak`` will be ignored in processing,
and we will get a comparison between ``I know`` (``\edtext`` content)
with ``I know that`` (context). This will match and hence correctly
annotate the phrase.

*Another example:* The script searches for words or phrases identical to
those in the ``\edtext{}{}`` macros to identify possible conflicts. By
default the content of practically all macros are included in this
comparison.

Take this passage:

.. code:: latex

    \edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: Sortes\test{2} probus

Will result in a search for “Sortes1” in the string “dicit Sortes2
probus”, which will not succeed.

On the other hand, this passage:

.. code:: latex

    \edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: Sortes\test{1} probus

Will result in a search for “Sortes1” in the string “dicit Sortes1
probus”, which will succeed and therefore annotate the instances.

If you add ``\test`` to the ``excluded_macros`` field, both examples
above will compare “Sortes” with “Sortes” and hence give a positive
match.

``ellipsis_patterns``
^^^^^^^^^^^^^^^^^^^^^

This key contains a list of patterns that should be included when
matching for ellipsis symbols in ``\lemma{}``. These are used in a
regular expression match, so any valid python regular expression will
work.

Say you use “–” and “…” to indicate ellipsis. Actually, you ought to
write the dotted ellipsis with ``\dots{}`` in ``LaTeX``, but if you
insist, you could give the key the following list (but you shouldn’t,
really. Use ``\dots{}``):

.. code:: json

    {
      "ellipsis_patterns": [
        "\\.\\.\\.",
        "-+"
      ]
    }

This looks complicated, but don’t worry. The “…” is matched with a regex
pattern, which requires us to escape the regular “.” – that would
normally look like this ``\.\.\.``. But since we also need to escape the
backslashes, they are doubly escaped.

The second is a lot simpler, it is just a regex that will match one or
more regular dashes in your text. Note that this comes with some danger
as it will match if your lemma contains a single dash, even though you
might not have thought of it as an “ellipsis”-dash. In these cases, its
better to be explicit and either use double dashes (``--``) or real
unicode en-dashes (``–``). It is also typographically much better.

Another example of a regex match pattern would be to match for the thin
space command in ``LaTeX``, which is ``\,``, which produces a space of
just 0.16667em. A comma is a meta-character in regex, so it would need
escaped, which would look like ``\\,``, but the backslash is also a
meta-character, so that needs escaping too. This means that to match the
literal expression ``\,`` the regex would look like this: ``\\\\,``. So
if we wanted to match the ``LaTeX`` expression ``\,-\,`` (thin space, a
dash, and another thin space), we would write the following regex:
``\\\\,-\\\\,``. But as we would probably want to match any length of
dashes, it could be improved to ``\\\\,-+\\\\,``.

``sensitive_context_match``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The value of the settings variable ``sensitive_context_match`` determines
whether the search for matches in the proximity is case sensitive. By default it
is case sensitive, which means that “Word” and “word” will not be annotated with
``\sameword{}``. If the value is set to ``false``, it will be case insensitive.

In JSON:

.. code:: json

    {
      "sensitive_context_match": false
    }

In that case “Word” and “word” would match and hence be annotated. This is a
sensible setting when lemma words are not lower cased in the critical
apparatus.

Notice that if you disable case sensitive matching you need to use the
configuration ``swcaseinsensitive`` when you load *Reledmac* (e.g.
``\usepackage[swcaseinsensitive]{reledmac}``). See also §6.3.2 of the `Reledmac
documentation
<https://mirrors.ctan.org/macros/latex/contrib/reledmac/reledmac.pdf>`__.

``context_distance``
^^^^^^^^^^^^^^^^^^^^

This determines the amount of words that will be compared with a match phrase at
either side of an ``\edtext{}{}`` entry. A normal length line rarely contains more
than 15 words, so the default of 20 should often be enough. If a layout with
every long lines is used, it may be necessary to increase it, while it may make
sense to reduce the distance if maybe a two column setup is used. But a bit too
many ``\sameword{}`` annotations really does no harm.


``punctuation``
^^^^^^^^^^^^^^^

Punctuation may be critical when adjacent to potential sameword matches. If
exotic punctuation is used it might not automatically be separated from the rest
of the word. By default all characters that are not punctuation
or ``\`` ``{`` or ``}`` is considered part of a word.

Currently the following groups of characters are considered punctuation:

- ``!"#$&\'()*+,-./:;<=>?@^_`|~–—[]`` – pretty regular punctuation.
- ``⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯`` – some odd brackets from the `Miscellaneous Mathematical
  Symbols A
  <https://unicode-table.com/en/blocks/miscellaneous-mathematical-symbols-a/>`_.
- All characters in `General Punctuation
  <https://unicode-table.com/en/blocks/general-punctuation/>`_.
- All characters in `Supplemental Punctuation <https://unicode-table.com/en/blocks/supplemental-punctuation/>`_.

If you use characters as punctuation that are not in any of these groups, you
can add them manually via the punctuation field. It can either be just the raw
characters, regular expression statements or Unicode codepoints (e.g.
``\u0101`` = ā) or ranges of Unicode codepoints (``\u0100—\u017F`` = the Latin
Extended A block). The ``\u`` tells Python that we are dealing with escaped
Unicode codepoints.

``multiword``
^^^^^^^^^^^^^

In cases where an ``\edtext{}{}`` macro contains a phrase, and there is a phrase
of that match in the context, it is usually possible to either annotate each
words of the phrase separately or all in one ``\sameword{}`` macro.

Default setting is ``False``, meaning that each word is annotated separately.

For example:

.. code-block:: text

    A word with \edtext{a word}{\Afootnote{another D}} after it.

If that is annotated with multiple ``\sameword{}`` macros, it will look like
this

.. code-block:: text

    \sameword{A} \sameword{word} with \edtext{\sameword[1]{a}
    \sameword[1]{word}}{\Afootnote{another D}} after it.

This will result in an apparatus note with the numbering “A² word²”. If it is
annotated with a single “multiword” annotation, it looks like this

.. code-block:: text

    \sameword{A word} with \edtext{\sameword[1]{a word}}{\Afootnote{another D}}
    after it.

This will result in an apparatus note withe the numbering “A word²”.

Which of these solutions is prefered usually a question of the individual taste
and intuition of the editor.

In some cases this may however lead to problems: When multiple levels of
``\edtext{}{}`` annotations are nested and are in need of disambiguation, this
might however lead to unexpected results where the apparatus note occurs as if
it were annotated with the words separately (e.g. “A² word²”). Furthermore,
there is a risk that these “multiword” annotations yield a result where the
beginning or end of a ``\edtext{}{}`` overlaps with that of a ``\sameword{}``.
This is invalid LaTeX and will therefore not compile. The separate sameword
annotations will never give this problem, so it is prefered as default with the
option of the editor to enable the slightly more risky multiword approach.
