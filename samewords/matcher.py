import re
from collections import namedtuple

from samewords.tokenize import Words, Registry, Word, Tokenizer, Macro
from samewords.brackets import Brackets
from samewords import settings

from typing import List

SearchWords = namedtuple('SearchWords', 'content ellipsis')

class Matcher:
    """
    Receives a wordlist and a registry and returns the wordlist annotated
    with samewords.
    """

    def __init__(self, words: Words, registry: Registry) -> None:
        self.words = words
        self.registry = registry

    def annotate(self):
        """
        Given a registry, determine whether there is a context match of
        the edtext lemma content for each entry and annotate accordingly.
        """
        for entry in self.registry:
            # Get data points for phrase start and end
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl'] + 1   # Reledmac 1-indexes the levels.
            edtext = self.words[edtext_start:edtext_end + 1]

            # Identify search words
            searches = self._define_search_words(edtext)

            # Establish the context
            context_before = self.words[edtext_start - 30:edtext_start]
            context_after = self.words[edtext_end + 1:edtext_end + 31]
            collected_context = context_before + context_after

            # Determine whether matcher function succeeds in either context.
            if self._find_match(collected_context, searches.content,
                                searches.ellipsis) is not -1:
                # If so, annotate the edtext element
                self._add_sameword(edtext, edtext_lvl)

                # Then annotate the two contexts
                for context in [context_before, context_after]:
                    if searches.ellipsis:
                        for word in searches.content:
                            self._annotate_context(context, word,
                                                   searches.ellipsis)
                    else:
                        self._annotate_context(context, searches.content,
                                               searches.ellipsis)
        return self.words

    def _annotate_context(self, context: List, searches: List,
                          ellipsis: bool) -> None:
        match_start = self._find_match(context, searches, ellipsis)
        if match_start is not -1:
            pos = match_start
            # Annotate all matches
            while True:
                end_pos = pos + len(searches)
                self._add_sameword(context[pos:end_pos], 0)
                new_pos = self._find_match(context, searches,
                                           ellipsis, start=end_pos + 1)
                if new_pos is not -1:
                    pos = new_pos
                else:
                    break

    def _add_sameword(self, chunk: Words, level: int):
        word: Word = chunk[0]

        # Should we handle the lemma level?
        if level is not 0:
            this_lvl = level
        else:
            this_lvl = ''

        # Is the phrase wrapped?
        sw_wrap = None
        lvl_match = None
        pat = re.compile(r'(\\sameword)([^{]+)?')
        sw_index = [i for i,val in enumerate(word.macros)
                    if re.search(pat, val.complete)]
        if sw_index:
            sw_match = re.search(pat, word.macros[sw_index[0]].complete)
            sw_wrap = sw_match.group(0)
            lvl_match = sw_match.group(2)

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
            sw_macro = Macro(r'\sameword' + this_lvl + '{')
        else:
            if this_lvl:
                sw_macro = Macro(r'\sameword[' + str(this_lvl) + ']{')
            else:
                sw_macro = Macro(r'\sameword{')

        if sw_wrap:
            word.macros[sw_index[0]] = sw_macro
        else:
            word.macros.append(sw_macro)
            chunk[-1].suffix += '}'
        chunk[0] = word

    def _find_match(self, context: List, searches: List, ellipsis: bool,
                    start: int = 0) -> int:
        """Return the position of the first match of search_words list in
        context. If no match is found, return -1 """
        def one_word(context: List, searches: List, start: int = 0) -> int:
            for word in searches:
                try:
                    return context[start:].index(word) + start
                except ValueError:
                    return -1

        def multi_word(context: List, searches: List, start: int = 0) -> int:
            try:
                match_start = context[start:].index(searches[0]) + start
                match_end = match_start + len(searches)
                if context[match_start:match_end] == searches:
                    return match_start
            except ValueError:
                return -1

        if ellipsis:
            return one_word(context, searches, start)
        else:
            return multi_word(context, searches, start)

    def _define_search_words(self, edtext: Words) -> SearchWords:
        """
        From the Words that make up the edtext element, determine the search
        words based on either (1) the content of the lemma element in the
        apparatus note or (2) the content of the critical note.

        :return: Cleaned list of search words (not Words, but their .text).
        """
        # The apparatus note is the first item in app_entries of last Word
        app_note = edtext[-1].app_list.pop()
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
            settings_pat = '|'.join(['({})'.format(pat) for pat
                                         in settings.ellipsis_patterns])
            ellipsis_pat = re.compile(r'(\\l?dots({})?)|' + settings_pat)
            if re.search(ellipsis_pat, lemma_content):
                # Covers ellipsis lemma.
                words = SearchWords(content= [lemma_word_list[0].text] + \
                                             [lemma_word_list[-1].text],
                                    ellipsis=True)
            elif len(lemma_word_list) == 1:
                # Covers single word lemma
                words = SearchWords(content=[lemma_word_list[0].text],
                                    ellipsis=False)
            elif len(lemma_word_list) > 1:
                # Covers multiword lemma
                words = SearchWords(content=lemma_word_list.clean(),
                                    ellipsis=False)
            else:
                words = SearchWords(content=[], ellipsis=False)
        else:
            words = SearchWords(content=edtext.clean(), ellipsis=False)
        return words
