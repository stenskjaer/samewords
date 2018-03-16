Samewords: Disambiguate words in critical editions
==================================================

In critical textual editions notes in the critical apparatus are
normally made to the line where the words occur. This leads to ambiguous
references when a critical apparatus note refers to a word that occurs
more than once in a line. For example:

::

    We have a passage of regular text here, such a nice place for a critical
    note.

    ----
    1 a] om. M

It is very unclear which of three instances of “a” the note refers to.

`Reledmac <https://www.ctan.org/pkg/reledmac>`__ is a great LaTeX package that
facilitates typesetting critical editions of prime quality. It already provides
facilities for disambiguating identical words, but it requires the creator of
the critical text to mark all potential instances of ambiguous references
manually (see the *reledmac* handbook for the details on that). *Samewords*
automates this step for the editor.

Installation
============

*Samewords* requires Python 3.6 installed in your system. If you are on
a Mac OSX machine, and you use `Homebrew <https://brew.sh/>`__, you can
run ``brew install python3``. If you do not use Homebrew (or run a
Windows machine), download the `latest official python
distribution <https://www.python.org/downloads/>`__ and follow the
instructions.

Easy installation
-----------------

.. code:: bash

    pip3 install samewords

That’s it!

Optional: Virtual environment
-----------------------------

Before installation you may want to create a virtual environment (`see
more here <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__)
for the installation, if you don’t want to install the script globally.
This is also particularly useful if you want to hack on the script.

To create a virtual environment for the project, run:

.. code:: bash

    $ mkvirtualenv -p python3 <name>

Where ``<name>`` is the name you want to give the venv.

After activating the virtual environment (``workon`` or ``source``, see
the guide linked above or search the interwebs), install the package.

For development
---------------

Download the repository:

::

    git clone https://github.com/stenskjaer/samewords.git

From the downloaded directory, run:

.. code:: bash

    $ pip install -e .

Now you should be able to run the script (while the virtual environment
is activated, if you used that) by running ``samewords``.

To see if it works, run:

.. code:: bash

    samewords --help

Your should get an overview of the commands available.

When you are done, you can reset your system to the state before
testing, deactivate the virtual environment. If you never want to use
the script again, remove the directory of the environment (possibly with
``rmvirtualenv`` if you have installed ``virtualenvwrapper``) and remove
the directory created by the ``git clone`` command.

If you want to make a pull request
~~~~~~~~~~~~~~~~~~

Before you start making any changes, run the test suite and make sure
everything passes. From the root directory of the package, run:

.. code:: bash

    pytest

If you make changes, don’t forget to implement tests and make sure
everything passes. Otherwise, things will break.

Usage
-----

Simple: Call the script with the file you want annotated as the only
argument to get the annotated version back in the terminal.

.. code:: bash

    samewords my-awesome-edition.tex

will send the annotated version to ``stdout``. To see that it actually
contains some ``\sameword{}`` macros, you can try running it through
``grep``:

.. code:: bash

    samewords my-awesome-edition.tex | grep sameword

You can define a output location with the ``--output`` option:

.. code:: bash

    samewords --output ~/Desktop/test/output my-awesome-edition.tex

will check whether ``~/Desktop/test/output`` is a directory or a file.
If it is a directory, it will put the file inside that directory (with
the original name). If it is a file, it will ask you whether you want to
overwrite it. If it is neither a directory nor a file, it will create
the file ``output`` and write the content to that.

Alternatively regular unix redirecting will work just as well in a Unix
context:

.. code:: bash

    samewords my-beautiful-edition.tex > ~/Desktop/test/output.tex


Aside from adding ``\sameword{}``-macros as appropriate the script also converts
all combined unicode characters into single point variants where they are
available. That means that if you compose 006F (o) and 0308 (̈) they will be
converted into the single code point 00F6 (ö). This ensures matching in these
ambiguous cases if the two systems should be mixed. On this, see `here
<https://en.wikipedia.org/wiki/Unicode_equivalence>`_


Cleaning and updating files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an edition has been annotated, but you want to make further changes to the
text, you don't have to keep track of which changes have consequences for the
``\sameword{}`` annotations.

You can either clean the text for any annotations with the ``--clean`` command
line argument or simply make your changes to the file with annotations and then
run the script with the ``--update`` to do exactly that. You don't have to worry
about updating existing annotations. But if you change a ``\edtext{}`` that has
a ``\lemma{}`` you of course need to update the lemma too.

There is an ``--annotate`` argument too, just for good measure, but the script
runs in that mode by default, so there is no need to use it under normal
circumstances.


Configuration file
~~~~~~~~~~~~~~~~~~

You can configure a small range of settings relevant for the processing.
This is done in a JSON-formatted file. You give the location of the
config file to the argument ``--config-file``. The script will
automatically look for a config file with the name
``~/.samewords.json``, so if you put it there, you won’t have to specify
the command line argument every time you call the script. That can be
very handy if you often need to use the same configuration.

The configuration file recognizes the following parameters: -
``exclude_macros`` - ``ellipsis_patterns`` - ``sensitive_context_match``

JSON requires backslashes to be escaped if you want to preserved them in
the string. You do that with another backslash, so ``\\`` will result in
a single backslash. You must remember this when noting ``TeX`` strings
or regular expressions that contain backslashes.

A complete configuration file could contain the following content:

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

For details, see below.

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

The value of the settings variable ``sensitive_proximity_match``
determines whether the search for matches in the proximity is case
sensitive. By default it is case insensitive, but if the value is set to
``True``, it will be case sensitive.

In JSON:

.. code:: json

    {
      "sensitive_context_match": true
    }

That would mean that the search for “an” in the context string “An
example” would not match. This is a sensible setting when lemma words
are not lower cased in the critical apparatus.

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
of the word (be default all characters that are not word characters, punctuation
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

If you feel bold you could of course edit the punctuation list in the settings
file.

Issue reporting and testing
===========================

If you like the idea of this software, please help improving it by
filing `issue report <https://github.com/stenskjaer/samewords/issues>`__
when you find bugs.

To file a bug
-------------

-  Create a *minimal working example* (MWE) TeX document that contains
   absolutely nothing aside from the material necessary for reproducing
   the bug. The document should (if possible) be able to compile on a
   fresh installation of LateX without any custom packages.
-  Open an `issue
   report <https://github.com/stenskjaer/samewords/issues>`__ and
   describe the conditions under which you experience the bug. It should
   be possible for me to reproduce the bug by following your directions.
-  If the script returns an error, copy and paste the error traceback
   into the report.
-  If the script returns you document, include that, and describe the
   result you expected, and how that differs from what you get.

Testing updated issue branches
------------------------------

Once I (think I) have a solution, I will ask you to test a branch. You
can do that by either downloading that specific branch as a zip or clone
the repository and pull down the changed branch. Choose one of the
following two, depending on you preferences.

**Downloading branch zip** This approach is simplest if (1) you don’t
feel quite comfortable using ``git`` or (2) only want to test a single
change or issue.

-  Navigate to the relevant branch in Github (the “Branch:” dropdown).
-  Download that branch to your computer (the “Clone or download”
   button).
-  Navigate to the downloaded zip file, unzip it and enter the
   directory.

**Clone repository and checkout branch** This approach is more flexible
and makes it easier for you to pull and test different branches. It also
makes it easier to keep track of which branch you are testing on (with
the ``git status`` command). Finally, if you should want to push changes
in pull requests, this is also the approach you should use.

-  Navigate to an appropriate directory.
-  Run ``git clone https://github.com/stenskjaer/samewords.git``. A
   directory with the name “samewords” will be created in you current
   working directory.
-  Check out the branch that you want to test. If that is called
   ``issue-13`` run ``git checkout issue-13``.

After either of the above processes, the rest is identical:
- Create a *virtual environment* for testing by running ``python3 -m venv
  .env``, and then activate it with ``source .env/bin/activate`` (this is based
  on a Unix environment, if you run Windows, check out `the Python documentation
  <https://docs.python.org/3.6/library/venv.html>`__).
- Install the script in the virtual environment with ``pip install -e .``.
- To make sure you run the version in the *virtual environment*, run
  ``.env/bin/samewords`` from the directory (to avoid using a global version of
  the script, if you have that).
- Run your supplied MWE (or other material provided by me in the issue report)
  and inspect whether the problem is solved and report back in the issue
  report.
- When you are done testing, deactivate the virtual environment by running
  ``deactivate`` (Bash on Unix) or ``deactivate.bat`` (Windows).

Notice that if you are asked to test a branch it is not necessary to run any of
the automated tests.

If you have downloaded a branch zip, you can delete the unzipped
directory, and everything should be back to normal.

If you have cloned the repository, you can just leave it there.

Disclaimer and license
======================

This is beta level software. Bugs are to be expected and I provide no
guarantees for the integrity of your software or editions when you use
the package.

Copyright (c) 2017 Michael Stenskjær Christensen, MIT License.
