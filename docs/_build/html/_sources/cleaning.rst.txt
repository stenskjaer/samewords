Cleaning and updating files
===========================

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
