#!/usr/bin/env python3
"""
Collection of functions for preparing LaTeX file for processing.

The main purpose is to provide the ability of identifying the relevant part of a reledmac-encoded LaTeX file and 
serve up content from each paragraph between `\beginnumbering` and `\endnumbering` for sameword processing. 

"""

def document_content(filename):
    """Return the content of file."""
    with open(filename) as f:
        return f.read()


def numbered_content(document_content):
    """
    Identify and return the text between `\beginnumbering` and `\endnumbering` of a string. 
    """
    start = document_content.find(r'\beginnumbering')
    end = document_content.find(r'\endnumbering')
    return document_content[start:end + len(r'\endnumbering')]


