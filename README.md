# Samewords: Disambiguate words in critical editions

In critical textual editions notes in the critical apparatus are normally made
to the line where the words occur. This leads to ambiguous references when a
critical apparatus note refers to a word that occurs more than once in a line.
For example:

```
We have a passage of regular text here, such a nice place for a critical note.

----
1 a] om. M
```

It is very unclear which of three instances of "a" the note refers to.

[Reledmac](https://www.ctan.org/pkg/reledmac) is a great LaTeX package that
facilitates typesetting critical editions of prime quality. It already provides
facilities for disambiguating identical words, but it requires the creator of
the critical text to manually mark all potential instances of ambiguous
references manually (see the *reledmac* handbook for the details on that).
*Samewords* automates this step for the editor.

# Installation

*Samewords* requires Python 3.6 installed in your system. If you are on a Mac
OSX machine, and you use [Homebrew](https://brew.sh/), you can run `brew install
python3`. If you do not use Homebrew (or run a Windows machine), download the
[latest official python distribution](https://www.python.org/downloads/) and
follow the instructions.

## Easy installation

```bash
pip3 install samewords
```

That's it!

## Optional: Virtual environment

Before installation you may want to create a virtual environment
([see more here](http://docs.python-guide.org/en/latest/dev/virtualenvs/)) for
the installation, if you don't want to install the script globally. This is also
particularly useful if you want to hack on the script.

To create a virtual environment for the project, run:
```bash
$ mkvirtualenv -p python3 <name>
```

Where `<name>` is the name you want to give the venv.

After activating the virtual environment (`workon` or `source`, see the guide
linked above or search the interwebs), install the package.

## For development

Download the repository:
```
git clone https://github.com/stenskjaer/samewords.git
```

From the downloaded directory, run: 
```bash 
$ pip install -e .
```

Now you should be able to run the script (while the virtual environment is
activated, if you used that) by running `samewords`. 

To see if it works, run:

```bash
samewords --help
```
Your should get an overview of the commands available. 

When you are done, you can reset your system to the state before testing,
deactivate the virtual environment. If you never want to use the script again,
remove the directory of the environment (possibly with `rmvirtualenv` if you
have installed `virtualenvwrapper`) and remove the directory created by the `git
clone` command.

### Remember the tests

Before you start making any changes, run the test suite and make sure everything
passes. From the root directory of the package, run:

```bash
pytest
```

If you make changes, don't forget to implement tests and make sure everything
passes. Otherwise, things will break.

## Usage ##

Simple: Call the script with the file you want annotated as the only argument to
get the annotated version back in the terminal. 

```bash
samewords my-awesome-edition.tex
```

will send the annotated version to `stdout`. To see that it actually contains
some `\sameword{}` macros, you can try running it through `grep`:

```bash
samewords my-awesome-edition.tex | grep sameword
```

You can define a output location with the `--output` option:
```bash
samewords --output ~/Desktop/test/output my-awesome-edition.tex
```
will check whether `~/Desktop/test/output` is a directory or a file. If it is a
directory, it will put the file inside that directory (with the original name).
If it is a file, it will ask you whether you want to overwrite it. If it is
neither a directory nor a file, it will create the file `output` and write the
content to that.

Alternatively regular unix redirecting will work just as well in a Unix context:
```bash
samewords my-beautiful-edition.tex > ~/Desktop/test/output.tex
```

### Include macros in disambiguations (`--include-macros`) ###

The script searches for words or phrases identical to those in the `\edtext{}{}`
macros to identify possible conflicts. Per default the content of practically
all macros are included in this comparison.

Take this passage:
```latex
\edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: Sortes\test{2} probus
```

Will result in a search for "Sortes1" in the string "dicit Sortes2 probus",
which will not succeed.

On the other hand, this passage:
```latex
\edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: Sortes\test{1} probus
```

Will result in a search for "Sortes 1" in the string "dicit Sortes 1 probus",
which will succeed and therefore annotate the instances.

You might want to distinguish some phrases based on their contained macros. For
instance you might want to let `Hákon\emph{ar}` and `Hákonar` be two different
strings. In that case you use the `--include-macros` argument.

`--include-macros` must point to a text file where each line contains a macro
that you want to keep in the comparison algorithm. So to distinguish
`Hákon\emph{ar}` from `Hákonar`, I would write the following text-file:

```txt
\emph
```

And then pass the location of that file in the argument `--include-macros`.

To see the details of this, see the `clean` function in the `annotate` module.

# Be advised

This is beta level software. Bugs are to be expected and I provide no
guarantees for the integrity of your software or editions when you use the
package.

This also means: Let me know when and how it breaks by filing
an [issue report](https://github.com/stenskjaer/samewords/issues). 
