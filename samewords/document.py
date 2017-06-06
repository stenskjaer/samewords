#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for preparing LaTeX file for processing.

The main purpose is to provide the ability of identifying the relevant part of a reledmac-encoded LaTeX file and 
serve up content from each paragraph between `\beginnumbering` and `\endnumbering` for sameword processing. 

TODO: This should also be able to handle more than one section of numbered text in the document.
"""

import re


def document_content(filename):
    """Return the content of file."""
    with open(filename, 'rb') as f:
        return f.read().decode('utf-8')


def chunk_document(content):
    """
    Split document into content before, inside and after `\beginnumbering` and `\endnumbering` and return dictionary.
    
    :param content: The content of the document as a string. 
    :return: Dictionary with three keys: { before : 'content', inside : 'content', after : 'content' }
    """
    start = content.find('\\beginnumbering\n') + len('\\beginnumbering\n')
    end = content.find('\n\\endnumbering')
    return {
        'before' : content[:start],
        'inside' : content[start:end],
        'after' : content[end:],
    }


def chunk_paragraphs(content):
    """Given the context contained between `\beginnumbering` and `\endnumbering`, return list of paragraphs.
    
    This is able to handle paragraphs demarcated by `\pstart` and `\pend` as well as when `\autopar` is used (see 
    §5.2.2 of the reledmac documentation). The use of `\autopar` assumes that the `\autopar` command is given right 
    after the `\beginnumbering` as in the documentation. 
    """

    if content.find(r'\autopar') is not -1:
        paragraph_positions = [pstart.start() for pstart in re.finditer('\n\n', content)]
    else:
        paragraph_positions = [pstart.start() for pstart in re.finditer(r'\\pstart', content)]

    paragraphs = []
    for index, par in enumerate(paragraph_positions):
        try:
            paragraphs.append(content[par:paragraph_positions[index + 1]])
        except IndexError:
            paragraphs.append(content[par:])

    return paragraphs
