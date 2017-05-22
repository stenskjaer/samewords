from samewords.core import *
import samewords.document as document

class TestMainProcessing:
    filename = './samewords/test/assets/da-49-l1q1.tex'
    processed_content = document.document_content('./samewords/test/assets/da-49-l1q1-processed.tex')

    def test_process_document(self):
        assert process_document(self.filename) == self.processed_content
