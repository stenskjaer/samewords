from samewords.document import *


def test_document_content():
    with open('./samewords/test/assets/da-49-l1q1.tex', 'rb') as f:
        content = f.read().decode('utf-8')
    assert doc_content('./samewords/test/assets/da-49-l1q1.tex') == content

multi_begins = doc_content('./samewords/test/assets/multi_begins.tex')

class TestDocumentChunking:

    def test_multiple_begin_numbers(self):

        content = [
            multi_begins[0:666],
            multi_begins[666:1734],
            multi_begins[1734:1797],
            multi_begins[1797:2865],
            multi_begins[2865:2928],
            multi_begins[2928:3996],
            multi_begins[3996:4077]
        ]
        # indices to numbered chunks in the content field
        assert chunk_doc(multi_begins) == content

    def test_no_numbered_text(self):
        document = doc_content('./samewords/test/assets/no_numbers.tex')
        assert chunk_doc(document) == [document]

class TestChunkParagraphs:

    chunks = chunk_doc(multi_begins)

    def test_single_chunk(self):
        pars = [
            '\\beginnumbering\n\n',
            '\\pstart[\\subsection*{\\metatext{De scientia}}]\n\\edlabelS{'
            'da-49-l1q1-274hkz}%\n\\ledsidenote{B 148va}\\ledsidenote{O '
            '164rb}%\n\\edtext{Item}{\\lemma{Item}\\Bfootnote{\\emph{om.} '
            'B}}\nquaeratur\\edtext{}{\\lemma{}\\Bfootnote[nosep]{nunc '
            '\\emph{post} quaeratur B}}\nprimo utrum de anima possit nobis '
            'acquiri scientia.\n\\edlabelE{da-49-l1q1-274hkz}\n\\pend\n\n',
            '\\pstart\n\\edlabelS{da-49-l1q1-mjzkyp}%\n\\no{1.2}\nPraeterea, '
            'unum et idem non potest esse simul movens et motum,'
            '\nquia\\edtext{}{\\lemma{}\\Bfootnote[nosep]{si \\emph{post} '
            'quia B}} sic \\edtext{idem\n  esset}{\\lemma{idem '
            'esset}\\Bfootnote{\\emph{inv.} B}} actu et potentia '
            'respectu\neiusdem; sed cognitum est movens respectu cognocentis; '
            'ergo unum et idem non\npotest esse \\edtext{cognoscens}{\\lemma{'
            'cognoscens}\\Bfootnote{movens B}} et\n\\edtext{cognitum}{'
            '\\lemma{cognitum}\\Bfootnote{motum\n    B}},\\edtext{}{\\lemma{'
            '}\\Bfootnote[nosep]{sed \\emph{post} motum B}} hoc '
            'tamen\ncontingeret si de anima \\edtext{esset scientia}{\\lemma{'
            'esset\n    scientia}\\Bfootnote{cognitionem haberemus '
            'B}}.\n\\edlabelE{da-49-l1q1-mjzkyp}\n\\pend\n\n\\endnumbering'
        ]
        assert chunk_pars(self.chunks[1]) == pars
