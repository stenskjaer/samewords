"""
This is the settings files. The variables hare are generally modified at
runtime (as command line arguments), but can also be modified manually in
here.
"""

exclude_macros = [
    r'\sidenote',
    r'\index',
    r'\thinspace',
    r'\enspace',
    r'\enskip',
    r'\quad',
    r'\qquad',
    r'\hskip',
    r'\negthinspace',
    r'\kern'
]

# List of patterns that should be included when matching for ellipsis symbols
#  in `\lemma{}`. These are used in a regular expression match, so any valid
# python regular expression will work.
ellipsis_patterns = [
    r'\\l?dots({})?',   # \dots, \dots{}, \ldots, \ldots{}
    '-+',               # one or more dashes
    '–',                # one or more en-dash
    '—'                 # em-dash
]

# Should the proximity search be case sensitive? That would mean that the
# search for "an" in the context string "An example" would not match. This is a
# good setting when lemma words are not lower cased in the critical apparatus.
sensitive_context_match = False
