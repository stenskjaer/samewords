from samewords.core import *
from samewords.settings import settings
import samewords.document as document


class TestMainProcessing:
    unprocessed = "./samewords/test/assets/da-49-l1q1.tex"
    processed = "./samewords/test/assets/da-49-l1q1-processed.tex"
    unproc_content = document.doc_content(unprocessed)
    proc_content = document.doc_content(processed)

    def test_process_document(self):
        assert process_document(self.unprocessed) == self.proc_content

    def test_update_document(self):
        unupdated = "./samewords/test/assets/simple-unupdated.tex"
        updated = "./samewords/test/assets/simple-updated.tex"
        updated_content = document.doc_content(updated)
        assert process_document(unupdated, "update") == updated_content

    def test_clean_document(self):
        assert process_document(self.processed, "clean") == self.unproc_content

    def test_process_string(self):
        assert process_string(self.unproc_content) == self.proc_content
