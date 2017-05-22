from samewords.document import *


def test_document_content():
    with open('./test/documents/da-49-l1q1.tex') as f:
        content = f.read()
    assert document_content('./test/documents/da-49-l1q1.tex') == content


def test_numbered_paragraphs():
    document = document_content('./test/documents/da-49-l1q1.tex')
    numbered = document_content('./test/documents/da-49-l1q1-numbered.tex')
    assert numbered_content(document) == numbered