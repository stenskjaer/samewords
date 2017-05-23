# Samewords: Disambiguate words in critical editions

In critical textual editions notes in the critical apparatus are normally made
to the line where the words occur. This leads to ambiguous references when a
critical apparatus note refers to a word that occurs more than once in a line.
For example:

```
We have a passage of regular text here, such a nice place for a critical note.

----
1 a] *om.* M
```

It is very unclear which of three instances of "a" the note refers to.

[Reledmac](https://www.ctan.org/pkg/reledmac) is a high quality package for
LaTeX that facilitates typesetting of critical editions of prime quality. It
already provides facilities for disambiguating identical words, but it requires
the creator of the critical text to manually mark all potential instances of
ambiguous references manually. *Samewords* automates this step for the editor.

# Installation

Download the repository. 
```
git clone https://github.com/stenskjaer/samewords.git
```

*Samewords* requires Python 3.6 installed in your system. If you are on a Mac
OSX machine, and you use [Homebrew](https://brew.sh/), you can run `brew install
python3`. If you do not use Homebrew (or run a Windows machine), download the
(latest official python distribution)[https://www.python.org/downloads/] and
follow the instructions.

## Testing

This solution is good for testing, development and if you would like to try out
the script without installing anything permanently on your system. 

You should create
a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
to avoid installing anything on your whole system. All the help you need should
be in the linked guide.

To create a virtual environment for the project, run:
```bash
$ mkvirtualenv -p python3 <name>
```

Where `<name>` is the name you want to give the venv.

After activating the virtual environment (`workon` or `source`), install
the package. From the root directory of the package (where `setup.py` is) run:

```bash 
$ pip install -e .
```

Now you should be able to run the script (while the virtual environment is
activated) by running `samewords`. 

To see if it works, run:

```bash
samewords --help
```
Your should get an overview of the commands available. 

To try converting a file, run the script with a *valid* reledmac encoded file.
If you don't have one lying around, try the one provided in the test suite by
running this command:

```bash
samewords ./samewords/test/assets/da-49-l1q1.tex
```

It should spit out an updated text. To see that it actually contains some
`\sameword{}` macros, you can try running it through `grep`:

```bash
samewords ./samewords/test/assets/da-49-l1q1.tex | grep sameword
```

When you are done, you can reset your system to the state before testing,
deactivate the virtual environment. If you never want to use the script again,
remove the directory of the environment (possibly with `rmvirtualenv` if you
have installed `virtualenvwrapper`) and remove the directory created by the `git
clone` command.

## System install

If you would like to install the script for general usage on you system, you
should run the command 
```bash
python3 setup.py install
```

Now try:
```bash
$ samewords <filename>
```
Where <filename> is the name of a file that you want to convert. 


## Development and contribution

Before you start making any changes, run the test suite and make sure everything
passes. From the root, run:

```bash
pytest
```

If you make changes, don't forget to implement tests and make sure everything
passes. Otherwise, things will break.

# Usage

`samewords --help` produces this output:
```
Samewords annotates potentially ambiguous words in critical text editions
made with LaTeX and reledmac.

Usage: samewords [options] <file>

Arguments:
  <file>                Location of local file to be processed.

Options:
  --output <location>   Location of output. You can specify a filename as part of
                        the address. If you don't do that, the name of the input
                        file will be used.
  -v, --version         Show version and exit.
  -h, --help            Show this help message and exit.

```

For now the package only has one option aside from the `--help/-h` and
`--version/-v`. Use `--output` to indicate in which folder of to which file you
want save the result.

For example:
```bash
samewords --output ~/Desktop/test/output my-beautiful-edition.tex
```
will check whether `~/Desktop/test/output` is a directory or a file. If it is a
directory, it will put the file inside that directory (with the original name).
If it is a file, it will ask you whether you want to overwrite it. If it is
neither a directory nor a file, it will create the file `output` and write the
content to that.

# Be advised

This is alpha level software. Bugs are to be expected and I provide no
guarantees for the integrity of your software or editions when you use the
package.
