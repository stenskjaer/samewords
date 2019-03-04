.. _installation:

Minial working example
======================

Take the following small example file as *our-edition.tex*

.. code-block:: text

    \documentclass{article}
    \usepackage[final]{reledmac}

    \begin{document}
    \beginnumbering

    \pstart
    We have a passage of text here, such \edtext{a}{\Afootnote{om. M}} nice
    place for a critical note.
    \pend

    \endnumbering
    \end{document}

If we annotate that with the command ``samewords our-edition.tex`` (in the same
directory as the file is) we get back the following result

.. code-block:: text

    \documentclass{article}
    \usepackage[final]{reledmac}

    \begin{document}
    \beginnumbering

    \pstart
    We have \sameword{a} passage of text here, such \edtext{\sameword[1]{a}}{\Afootnote{om. M}} nice
    place for \sameword{a} critical note.
    \pend

    \endnumbering
    \end{document}

Notice how the three instances of “a” have been wrapped in a ``\sameword{}``
macro.

If we run the command ``samewords our-edition.text --output annotated-version.tex``
then the annotated version is saved to the file “annotated-version.tex” in the
current directory.