"""
This is the settings files. The variables hare are generally modified at
runtime (as command line arguments), but can also be modified manually in
here.
"""

settings = {
    'exclude_macros': [
        r'\sidenote',
        r'\index',
        r'\thinspace',
        r'\,',
        r'\enspace',
        r'\enskip',
        r'\quad',
        r'\qquad',
        r'\hskip',
        r'\negthinspace',
        r'\kern'
    ],

    # List of patterns that should be included when matching for ellipsis symbols
    #  in `\lemma{}`. These are used in a regular expression match, so any valid
    # python regular expression will work.
    'ellipsis_patterns': [
        r'\\l?dots({})?',   # \dots, \dots{}, \ldots, \ldots{}
        '-+',               # one or more dashes
        '–',                # one or more en-dash
        '—'                 # em-dash
    ],

    # Should the proximity search be case sensitive? That would mean that the
    # search for "an" in the context string "An example" would not match. This is a
    # good setting when lemma words are not lower cased in the critical apparatus.
    'sensitive_context_match': True,

    # The content search distance determines how many words before and after and
    # entry should be compared. A normal length line rarely contains more than 15
    #  words, so the default of 20 should often be enough. If a layout with every
    #  long lines is used, it may be necessary to increase it.
    'context_distance': 20,

    # Additional punctuation characters can be added here. It can either be
    # just the raw characters, regular expression statements or Unicode
    # escaped codepoints (e.g. \u0101 = ā) or ranges of Unicode codepoints (
    # \u0100—\u017F = the Latin Extended A block).
    'punctuation': [
        r'!"#$&\'()*+,-./:;<=>?@^_`|~–—\[\]',    # general punctuation
        r'⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯',          # special brackets from the Misc Mat. Symbols A
        r'\u2000-\u206F',    # General punctuation (≠ the punctuation above)
        r'\u2e00-\u2e7f',    # Supplemental punctuation
    ]
}
