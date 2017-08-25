#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import samewords.annotate as annotate
import samewords.document as document


def process_document(filename):
    """
    The function directing the processing of a document. Return updated
    document as string.
    """

    document_content = document.document_content(filename)
    chunked_document = document.chunk_document(document_content)
    paragraphs = document.chunk_paragraphs(chunked_document['inside'])
    updated_paragraphs = [
        annotate.critical_note_match_replace_samewords(par)
        for par in paragraphs
    ]

    return chunked_document['before'] + ''.join(
        updated_paragraphs) + chunked_document['after']
