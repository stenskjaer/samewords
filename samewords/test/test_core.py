from samewords.core import *
from samewords import settings
import samewords.document as document


class TestMainProcessing:
    filename = './samewords/test/assets/da-49-l1q1.tex'
    processed_content = document.doc_content(
        './samewords/test/assets/da-49-l1q1-processed.tex')

    def test_process_document(self):
        settings.sensitive_context_match = True
        assert process_document(self.filename) == self.processed_content
        settings.sensitive_context_match = False
