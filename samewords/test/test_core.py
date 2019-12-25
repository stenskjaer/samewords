import os

from samewords.test import __testroot__
from samewords.core import *
from samewords import document

unprocessed = os.path.join(__testroot__, "assets/da-49-l1q1.tex")
processed = os.path.join(__testroot__, "assets/da-49-l1q1-processed.tex")


class TestMainProcessing:
    unproc_content = document.doc_content(unprocessed)
    proc_content = document.doc_content(processed)

    def test_process_document(self):
        assert process_document(unprocessed) == self.proc_content

    def test_update_document(self):
        unupdated = os.path.join(__testroot__, "assets/simple-unupdated.tex")
        updated = os.path.join(__testroot__, "assets/simple-updated.tex")
        updated_content = document.doc_content(updated)
        assert process_document(unupdated, "update") == updated_content

    def test_clean_document(self):
        assert process_document(processed, "clean") == self.unproc_content

    def test_process_string(self):
        assert process_string(self.unproc_content) == self.proc_content
