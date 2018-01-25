#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
import samewords.document as document


def run_annotation(input_text: str) -> str:
    tokenization = Tokenizer(input_text)
    matcher = Matcher(tokenization.wordlist, tokenization.registry)
    words = matcher.annotate()
    return words.write()


def process_document(filename: str) -> str:
    """The function directing the processing of a document. Return updated
    document as string. """

    document_content = document.document_content(filename)
    chunked_document = document.chunk_document(document_content)
    paragraphs = document.chunk_paragraphs(chunked_document['inside'])
    updated_paragraphs = [run_annotation(par) for par in paragraphs]

    return (chunked_document['before'] +
            ''.join(updated_paragraphs) +
            chunked_document['after'])
