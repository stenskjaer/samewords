For development
===============

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
----------------------------------

Before you start making any changes, run the test suite and make sure
everything passes. From the root directory of the package, run:

.. code:: bash

    pytest

If you make changes, don’t forget to implement tests and make sure
everything passes. Otherwise, things will break.
