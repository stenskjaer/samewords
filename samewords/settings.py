"""
This is the settings files. The variables hare are generally modified at
runtime (as command line arguments), but can also be modified manually in
here.
"""


exclude_macros = [
    '\\Afootnote',
    '\\Bfootnote',
    '\\Cfootnote',
    '\\Dfootnote',
    '\\Efootnote',
    '\\lemma',
    '\\applabel',
    '\\sidenote',
]

# Macros that should be included when identifying matches
include_macros = [
    # because Sortes\index[persons]{Socrates} ≠ Sortes\index[persons]{Sortes}
    '\\index',
]

# List of patterns that should be included when matching for ellipsis symbols
#  in `\lemma{}`. These are used in a regular expression match, so any valid
# python regular expression will work.
ellipsis_patterns = [
    '-+',  # one or more dashes
    '–',  # en-dash
    '—'  # em-dash
]
