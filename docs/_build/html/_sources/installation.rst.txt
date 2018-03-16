.. _installation:

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

