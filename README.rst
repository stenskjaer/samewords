Samewords
=========
.. image:: https://readthedocs.org/projects/samewords/badge/?version=latest
   :target: http://samewords.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

*Word disambigutaion in critical text editions*

In critical textual editions notes in the critical apparatus are
normally made to the line where the words occur. This leads to ambiguous
references when a critical apparatus note refers to a word that occurs
more than once in a line. For example:

::

    We have a passage of text here, such a nice place for a critical
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

Install and usage
-----------------

.. code:: bash

    pip3 install samewords

That’s it!

This requires Python 3.6 installed in your system. For more details on
installation, see the :ref:`installation` section.


Now call the script with the file you want annotated as the only argument to get
the annotated version back in the terminal.

.. code:: bash

    samewords my-awesome-edition.tex

This will send the annotated version to ``stdout``. To see that it actually
contains some ``\sameword{}`` macros, you can try running it through
``grep``:

.. code:: bash

    samewords my-awesome-edition.tex | grep sameword

You can define a output location with the ``--output`` option:

.. code:: bash

    samewords --output ~/Desktop/test/output my-awesome-edition.tex

This will check whether ``~/Desktop/test/output`` is a directory or a file.
If it is a directory, it will put the file inside that directory (with
the original name). If it is a file, it will ask you whether you want to
overwrite it. If it is neither a directory nor a file, it will create
the file ``output`` and write the content to that.

Alternatively regular unix redirecting will work just as well in a Unix
context:

.. code:: bash

    samewords my-beautiful-edition.tex > ~/Desktop/test/output.tex

See more in the `documentation <https://samewords.readthedocs.io/en/latest/>`__.
