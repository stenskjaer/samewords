import re

from samewords.tokenize import Words, Registry, RegistryEntry, Tokenizer
from samewords.brackets import Brackets
from samewords import settings

from typing import List


class Matcher:
    """
    Receives a wordlist and a registry and returns the wordlist annotated
    with samewords.
    """

    def __init__(self, words: Words, registry: Registry) -> None:
        self.words = words
        self.registry = registry
        self.ellipsis_lemma = False

    def annotate(self):
        """
        Given a registry, determine whether there is a context match of
        the edtext lemma content for each entry and annotate accordingly.
        """
        for entry in self.registry:
            # Get data points for phrase start and end
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = self.words[edtext_start:edtext_end + 1]

            # Identify search words
            search_words = self._define_search_words(edtext)

            # Establish the context
            context_before = self.words[edtext_start - 30:edtext_start]
            context_after = self.words[edtext_end + 1:edtext_end + 31]

            # Determine whether matcher function succeeds in either context.
            for context in [context_before, context_after]:
                if self._find_match(context, search_words) is not -1:
                    # First annotate the edtext item
                    self._add_sameword(edtext_start, edtext_end, edtext_lvl)

    def _add_sameword(self, start_index, end_index, level: int):
        word = self.words[start_index]

        # Should we handle the lemma level?
        if level is not 0:
            this_lvl = level
        else:
            this_lvl = ''

        # Is the phrase wrapped?
        sw_wrap = None
        lvl_match = None
        pre_sw = ''
        post_sw = ''
        sw_match = re.search(r'(\\sameword)([^{]+)?', word.macro.complete)
        if sw_match:
            sw_wrap = sw_match.group(0)
            lvl_match = sw_match.group(2)
            pre_pos = word.macro.find(r'\sameword')
            pre_sw = word.macro.complete[:pre_pos]
            post_sw = word.macro.complete[pre_pos + len(sw_wrap) + 1:]

        if sw_wrap:
            if lvl_match:
                # Peel of the wrapping brackets
                lvl_match = lvl_match[1:-1]
                # Wrap contains level indication
                if this_lvl:
                    # If we have a lemma level, combine with existing level.
                    lvl_set = set(
                        [int(i) for i in lvl_match.split(',')] + [this_lvl])
                    this_lvl = ','.join([str(i) for i in lvl_set])
                else:
                    # If lemma level of current annotation is None, keep the
                    # existing level argument.
                    this_lvl = lvl_match
            if this_lvl:
                this_lvl = '[' + str(this_lvl) + ']'
            sw_macro = r'\sameword' + this_lvl + '{'
        else:
            if this_lvl:
                sw_macro = r'\sameword[' + str(this_lvl) + ']{'
            else:
                sw_macro = r'\sameword{'

        word.macro.complete = pre_sw + sw_macro + post_sw

        self.words[start_index] = word
        if not sw_match:
            self.words[end_index].suffix += '}'

    def _find_match(self, context: List, search_words: List):
        """Return the position of the first match of search_words list in
        context. If no match is found, return -1 """
        try:
            match_start = context.index(search_words[0])
            if context[match_start:len(search_words)] == search_words:
                return match_start
        except ValueError:
            return -1
        return -1

    def _define_search_words(self, edtext: Words) -> List[str]:
        """
        From the Words that make up the edtext element, determine the search
        words based on either (1) the content of the lemma element in the
        apparatus note or (2) the content of the critical note.

        :return: Cleaned list of search words (not Words, but their .text).
        """
        # The apparatus note is the first item in app_entries of last Word
        app_note = edtext[-1].app_entries.pop(0)
        lemma_pos = app_note.find(r'\lemma')
        if lemma_pos is not -1:
            start = lemma_pos + len(r'\lemma')
            end = start + len(Brackets(app_note, start=start))
            # Content excluding the brackets
            lemma_content = app_note[start + 1:end - 1]
        else:
            lemma_content = ''

        if lemma_content:
            lemma_word_list = Tokenizer(lemma_content).wordlist
            settings_pattern = ''.join(['|({})'.format(pat) for pat
                                         in settings.ellipsis_patterns])
            ellipsis_pattern = re.compile(r'(\\l?dots({})?)' + settings_pattern)
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
