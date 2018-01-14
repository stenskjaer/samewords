import re

from samewords.tokenize import Words, Registry, Tokenizer
from samewords.brackets import Brackets
from samewords import settings

from typing import List


class Matcher:
    """
    Receives a wordlist and a registry and returns the wordlist annotated
    with samewords.
    """

    def __init__(self, words: Words, reg: Registry) -> None:
        self.words = words
        self.reg = reg
        self.ellipsis_lemma = False

    def annotate(self) -> Words:
        """
        Given the input word list, find sameword matches and return the
        annotated version of the list.
        """
        for entry in self.reg:
            # Get data points for phrase start and end and the edtext level
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = self.words[edtext_start:edtext_end + 1]

            # Identify search words
            search_words = self._define_search_words(edtext)

            # Get the context list before and after edtext

            # Match presence of the lemma in context

            # If match in context, annotate

        return self.words

    def _define_search_words(self, edtext: Words) -> List[str]:
        """
        From the Words that make up the edtext element, determine the search
        words based on either (1) the content of the lemma element in the
        apparatus note or (2) the content of the critical note.

        :return: Cleaned list of search words (not Words, but their .text).
        """
        def add_ellipses(patterns: List[str]) -> str:
            return ''.join(['|({})'.format(pat) for pat in patterns])

        def get_lemma_content(app_note: str) -> str:
            lemma_pos = app_note.find(r'\lemma')
            if lemma_pos is not -1:
                start = lemma_pos + len(r'\lemma')
                end = start + len(Brackets(app_note, start=start))
                # Content excluding the brackets
                return app_note[start + 1:end - 1]
            return ''

        # The apparatus note is the first item in app_entries of last Word
        app_note = edtext[-1].app_entries.pop(0)
        lemma_content = get_lemma_content(app_note)

        if lemma_content:
            lemma_word_list = Tokenizer(lemma_content).wordlist
            ellipsis_pattern = re.compile(
                r'(\\l?dots({})?)' + add_ellipses(settings.ellipsis_patterns))
            if re.search(ellipsis_pattern, lemma_content):
                # Covers ellipsis lemma.
                search_words = [lemma_word_list[0].text] + \
                               [lemma_word_list[-1].text]
                self.ellipsis_lemma = True
            elif len(lemma_word_list) == 1:
                # Covers single word lemma
                search_words = [lemma_word_list[0].text]
            elif len(lemma_word_list) > 1:
                # Covers multiword lemma
                search_words = lemma_word_list.clean()
            else:
                search_words = []
        else:
            search_words = edtext.clean()
        return search_words
