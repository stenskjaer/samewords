import pickle

import pytest

from samewords.document import *


class TestDocumentOpening:
    def test_ensure_unicode(self, tmpdir):
        f_name = tmpdir.mkdir('sub').join('cp1252.txt')
        f_content = 'Cœur ‰'
        with open(f_name, encoding='cp1252', mode='w') as f:
            f.write(f_content)

        assert open(f_name, encoding='cp1252').encoding == 'cp1252'
        assert open(f_name, mode='rb').read() == b'C\x9cur \x89'
        with pytest.raises(ValueError):
            document_content(f_name)

    def test_normalization(self, tmpdir):
        decomp_content = unicodedata.normalize(
            'NFD', 'μῆνιν ἄειδε, θεά, Πηληϊάδεω Ἀχιλῆος')
        comp_content = unicodedata.normalize(
            'NFC', 'μῆνιν ἄειδε, θεά, Πηληϊάδεω Ἀχιλῆος')

        p = tmpdir.mkdir("sub").join("decomp.txt")
        p.write(decomp_content)
        assert p.read() == decomp_content
        assert len(unicodedata.normalize('NFD', p.read())) == 43
        assert document_content(p) == comp_content


class TestParagraphHandling:

    pickle_jar = 'samewords/test/assets/pickles/'
    document = document_content('./samewords/test/assets/da-49-l1q1.tex')
    numbered = document_content(
        './samewords/test/assets/da-49-l1q1-numbered.tex')
    numbered_autopar = document_content(
        './samewords/test/assets/da-49-l1q1-numbered-autopar.tex')

    def test_chunk_document(self):
        chunked_dict = pickle.load(open(self.pickle_jar + 'chunked_document.pickle', 'rb'))
        assert chunk_document(self.document) == chunked_dict

    def test_get_numbered_paragraphs(self):
        assert chunk_document(self.document)['inside'] == self.numbered

    def test_chunk_pstart_paragraph(self):
        pstart_list = pickle.load(open(self.pickle_jar + 'pstart_list.pickle', 'rb'))
        assert chunk_paragraphs(self.numbered) == pstart_list

    def test_chunk_autopar_paragraph(self):
        autopars = pickle.load(open(self.pickle_jar + 'autopar_list.pickle', 'rb'))
        assert chunk_paragraphs(self.numbered_autopar) == autopars
