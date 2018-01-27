#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for preparing LaTeX file for processing.

The main purpose is to provide the ability of identifying the relevant part
of a reledmac-encoded LaTeX file and serve up content from each paragraph
between `\beginnumbering` and `\endnumbering` for sameword processing.
"""

import re
from typing import Dict
import unicodedata

from typing import List


def doc_content(filename: str) -> str:
    """Return the content of file."""

    with open(filename, mode='r', encoding='utf-8') as f:
        try:
            return unicodedata.normalize('NFC', f.read())
        except UnicodeDecodeError as e:
            raise ValueError(
                'The input file must be in utf-8 unicode encoding.') from e


def chunk_doc(content: str) -> List[str]:
    """
    Split document into a list of chunks. All unequal numbered indices are
    numbered text.

    :param content: The content of the document as a string.
    """
    starts = re.finditer(r'\\beginnumbering\n', content)
    ends = re.finditer(r'\n\\endnumbering', content)
    if '\\beginnumbering\n' in content:
        indices = []
        for start, end in zip(starts, ends):
            if not indices:
                # Setup the indices with the slice before first numbered text
                indices.append([0, start.span()[0]])
            else:
                # Add the indices between previous numbered section and next
                indices.append([indices[-1][-1], start.span()[0]])
            # Now, add the indices of the numbered section
            indices.append([start.span()[0], end.span()[1]])
        # Add the tail from last numbered to end
        indices.append([indices[-1][-1], len(content)+1])
        # Chunk the text according to the indices
        chunked = [content[start:end] for start, end in indices]
    else:
        chunked = [content]
    return chunked

def chunk_pars(content):
    """Given the context contained between `\beginnumbering` and
    `\endnumbering`, return list of paragraphs.

    This is able to handle paragraphs demarcated by `\pstart` and `\pend` as
    well as when `\autopar` is used (see §5.2.2 of the reledmac
    documentation). The use of `\autopar` assumes that the `\autopar` command
    is given right after the `\beginnumbering` as in the documentation.
    """

    if content.find(r'\autopar') is not -1:
        positions = [idx.start() for idx in re.finditer('\n\n', content)]
    else:
        positions = [idx.start() for idx in re.finditer(r'\\pstart', content)]

    paragraphs = []
    paragraphs.append(content[:positions[0]])
    for index, par in enumerate(positions):
        try:
            paragraphs.append(content[par:positions[index + 1]])
        except IndexError:
            paragraphs.append(content[par:])

    return paragraphs
