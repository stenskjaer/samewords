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
-  If the script returns an error, copy and paste the error reporting
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

- Create a *virtual environment* for testing with ``python3 -m venv .env``, and
  then activate it with ``source .env/bin/activate`` (this is based on a Unix
  environment, if you run Windows, check out `the Python documentation
  <https://docs.python.org/3.6/library/venv.html>`__).
- Install the script in the virtual environment with ``pip install -e .``.
- To make sure you run the version in the *virtual environment*, run
  ``.env/bin/samewords`` from the directory (to avoid using a global version of
  the script, if you have that).
- Run your supplied MWE (or other material provided by me in the issue report)
  and inspect whether the problem is solved and report back in the issue report.
- When you are done testing, deactivate the virtual environment by running
  ``deactivate`` (Bash on Unix) or ``deactivate.bat`` (Windows).

Notice that if you are asked to test a branch it is not necessary to run any of
the automated tests.

If you have downloaded a branch zip, you can delete the unzipped
directory, and everything should be back to normal.

If you have cloned the repository, you can just leave it there.
