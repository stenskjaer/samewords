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

[Reledmac](https://www.ctan.org/pkg/reledmac) is a high quality package for
LaTeX that facilitates typesetting of critical editions of prime quality. It
already provides facilities for disambiguating identical words, but it requires
the creator of the critical text to manually mark all potential instances of
ambiguous references manually. *Samewords* automates this step for the editor.

## Note

This current alpha version requires all `\edtext{}{}` elements to contain a
`\lemma{}` element in their second argument. This should not be required, but
currently is (see [issue #2](https://github.com/stenskjaer/samewords/issues/2)).

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

# Implementation details

## Marking ambiguouities in *reledmac*

The nature of LaTeX means that we cannot know before compilation how the
paragraphs and lines will be built. This means that we cannot predict which
words might end up on the same line. *Reledmac* adds numbers (or other symbols)
to indicate the position of an ambiguous word in an apparatus note. But to be
able to do that, we need to tell it which words have a risk of ending up on the
same line. This is done with the `\sameword{}` macro.

A critical apparatus note is created with the `\edtext{}{}` macro. The first
argument is the text printed in the main text and the second argument contains
information and content for the apparatus note. When the content of the first
argument contains a word that is marked by the `\sameword{}` macro, it check how
many instances of `\sameword{}` in the same line contain the identical word and
number the content of the apparatus accordingly.

The above example should thus be encoded like this:

``` 
We have \sameword{a} passage of regular text here, such
\edtext{\sameword{a}}{\Afootnote{\emph{om.} M}} nice place for \sameword{a}
critical note. 
``` 

Resulting in this apparatus note:
```
1 a²] om. M
```

## The general approach

The goal of *samewords* is therefore to identify all situations where there is a
risk of such collisions and mark the appropriate word in the `\edtext{}` and
surrounding content with `\sameword{}`.

At a very general level, this is done in the following way:
- For each `\edtext{}{}` command read the content of the `\lemma{}` command in
  the second argument (e.g. "maintext content" in `\edtext{maintext
  content}{\lemma{maintext content}\Afootnote{note content}}`)
  - If it only contains a single word, see if that word occurs in the immediate
    context.
  - If it contains a phrase with a variation of `\dots{}` (specifically the
    regex pattern `\l?dots({})?`), see of the content on each side of the dots
    is present in the immediate context.
  - If it contains more than one word (but not any dots), see if that exact
    phrase is present in the immediate context.
- When one of these conditions match in the proximate context, mark the search
  word in context and apparatus note with the `\sameword{}` macro.

The immediate content is for now defined as at least 30 words before and after
the current search word. This may be too much for many use cases, and could
therefore produce way too many annotated `\sameword{}`s, so customizing this
value is a planned feature.

This approach also requires that all apparatus notes contain a `\lemma{}`
command. Removing this requirement is also a planned feature.

## The challenges

At the face of it this seems simple. But any `\edtext{}{}` command can contain
an arbitrary number of nested `\edtext` commands, and each level can in itself
contain any amount of `\edtext{}{}` commands interspersed with regular text and
other LaTeX commands. 

The processing and annotation functions are therefore recursive. This means that
every time *samewords* encounters a `\edtext` command, it checks whether that
command contains any further `\edtext` commands, if that is the case, it
registers the proximate context surrounding the nested note end processes that
inner `\edtext` command, continuing like this until it finds the deepest
`\edtext` command and works its way out from there. 

This means that the context of level one apparatus note may be processed several
times, as any apparatus note needs search the context for the content of *that*
note.

This possibility of nesting the notes also means that for *reledmac* to annotate
and count the disambiguations correctly, we must indicate at which level words
that are contained in the first argument of an `\edtext{}` are referred to from
a `\lemma{}` (for more on this, see §6.3 of the [reledmac
documentation](http://mirrors.ctan.org/macros/latex/contrib/reledmac/reledmac.pdf)).
We therefore need to keep track of at which level the note that we process is,
independently of at which level the identical word of a `\edtext{}` element is
found. 

If, for example, a level one critical note contains the word *my* but the note
also contains a further note with that word, we need to mark both words with
`\sameword{}`, but also tell *reledmac* which of the two is referenced by the
`\lemma{}`. This could look like this:

```latex
I have found \edtext{\sameword[1]{my} keys in
\edtext{\sameword[2]{my}}{\lemma{my}\Afootnote{a B}} pocket}{\lemma{\sameword{my} \ldots{}
pocket}\Afootnote{the keys V}}.
```

Here the `[1]` in the first `\sameword{}` shows that *this* instance of “my” is
referenced from a level one `\lemma{}` while the `[2]` of the second
`\sameword{}` shows that *that* instance of “my” is referenced from a `\lemma{}`
at level two. It can get a bit more complicated than that, but see the
*reledmac* documentation for reference.

This challenge is solved by keeping a tally of the level at which any processing
takes it starting point. If we are below level one, these markers are added
where appropriate.

 
