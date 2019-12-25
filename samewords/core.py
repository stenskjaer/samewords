#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
from samewords.document import chunk_pars, chunk_doc, doc_content


def process_document(filename: str, method: str = "annotate") -> str:
    """The function directing the processing of a document. Return updated
    document as string."""

    content = doc_content(filename)
    return process_string(content, method=method)


def process_string(content: str, method: str = "annotate") -> str:
    """Process an input string. Return updated document as string."""

    chunked_content = chunk_doc(content)
    updated = []
    for i, chunk in enumerate(chunked_content):
        # Only unequal indices contain numbered reledmac paragraphs
        if not i % 2 == 0:
            chunk = "".join([run_annotation(par, method) for par in chunk_pars(chunk)])
        updated.append(chunk)

    return "".join(updated)


def run_annotation(input_text: str, method: str = "annotate") -> str:
    tokenization = Tokenizer(input_text)
    matcher = Matcher(tokenization.wordlist, tokenization.registry)
    if method == "annotate":
        words = matcher.annotate()
    elif method == "update":
        words = matcher.update()
    else:
        words = matcher.cleanup()
    return words.write()
