import re

from samewords.tokenize import Words, Registry, Word, Tokenizer, Macro
from samewords.brackets import Brackets
from samewords import settings

from typing import List, Tuple, Union


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
            search_ws, ellipsis = self._define_search_words(edtext)

            # Establish the context
            context_before = self._get_context_before(self.words, edtext_start)
            context_after = self._get_context_after(self.words, edtext_end + 1)
            contexts = ([w.get_text() for w in context_before]
                        + [w.get_text() for w in context_after])

            # Determine whether matcher function succeeds in either context.
            if search_ws and self._in_context(contexts, search_ws, ellipsis):
                # If so, annotate the edtext element, or parts of it, correctly.
                if ellipsis:
                    if search_ws[0] in contexts:
                        self._add_sameword(edtext[0:1], edtext_lvl)
                    if search_ws[-1] in contexts:
                        self._add_sameword(edtext[-1:], edtext_lvl)
                else:
                    sidx, eidx = self._find_index(edtext, search_ws)
                    self._add_sameword(edtext[sidx:eidx], edtext_lvl)

                # Then annotate the two contexts
                for context in [context_before, context_after]:
                    if ellipsis:
                        if search_ws[0] in context:
                            self._annotate_context(context, search_ws[0:1])
                        if search_ws[-1] in context:
                            self._annotate_context(context, search_ws[-1:])
                    else:
                        self._annotate_context(context, search_ws)
        return self.words

    def _get_context_after(self, complete: Words, boundary: int) -> Words:
        distance = 30
        start = boundary
        end = start
        count = 0
        while count < distance and end < len(complete):
            w: Word = complete[end]
            end += 1
            if w.content:
                count += 1
        return complete[start:end]

    def _get_context_before(self, complete: Words, boundary: int) -> Words:
        distance = 30
        end = boundary
        start = end
        count = 0
        while count < distance and start > 0:
            w: Word = complete[start]
            start -= 1
            if w.content:
                count += 1
        return complete[start:end]

    def _annotate_context(self, context: Words, searches: List) -> None:
        indices = self._find_index(context, searches)
        if indices:
            # Annotate all matches
            while True:
                start = indices[0]
                end = indices[1]
                self._add_sameword(context[start:end], 0)
                new_indices = self._find_index(context, searches, start=end + 1)
                if new_indices:
                    indices = new_indices
                else:
                    break

    def _add_sameword(self, part: Words, level: int) -> Words:
        """
        Wrap the `part` of words in a sameword macro with level indication,
        depending on some circumstances. If it is already wrapped in its
        entirety, we only update the sameword macro if necessary. If the
        level of an existing wrap is the same as the current, no change is
        made, otherwise that is updated.
        """
        word: Word = part[0]

        # Should we handle the lemma level?
        if level is not 0:
            this_lvl = level
        else:
            this_lvl = ''

        # Is the phrase wrapped?
        sw_wrap = None
        lvl_match = None
        pat = re.compile(r'(\\sameword)([^{]+)?')
        sw_idx = [i for i, val in enumerate(word.macros)
                  if re.search(pat, val.full())]
        try:
            sw_idx = sw_idx[0]
        except IndexError:
            sw_idx = -1

        # If the first word is wrapped, and it is equal in length to the
        # current chunk, then this chunk is already wrapped in its entirety,
        # and should not be rewrapped. In that case we update the wrap data.
        if sw_idx is not -1 and word.macros[sw_idx].to_closing == len(part) - 1:
            sw_match = re.search(pat, word.macros[sw_idx].full())
            sw_wrap = sw_match.group(0)
            lvl_match = sw_match.group(2)

        # If the whole phrase is wrapped, get data from that wrap and update it.
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
            word.update_macro(sw_macro, sw_idx)

        # Otherwise, build the macro and put correctly into first word's macros.
        else:
            if this_lvl:
                sw_macro = Macro(r'\sameword[' + str(this_lvl) + ']{')
            else:
                sw_macro = Macro(r'\sameword{')

            # If the first word already has a sameword wrap, put new one first.
            if sw_idx is not -1:
                word.add_macro(sw_macro, sw_idx)
            # Otherwise, put it at the end of macros (making it the innermost).
            else:
                word.add_macro(sw_macro)

            # Add closing bracket to last word.
            part[-1].append_suffix('}')
            # And register its distance.
            word.close_macro(len(part) - 1)

        # Update the first word
        part[0] = word
        return part

    def _in_context(self, context: Union[List[str], Words], searches: List,
                    ellipsis: bool) -> bool:
        """Determine whether there is a match, either of a one- or multiword
        sequence or the first or last word in the sequence, in case it is an
        ellipsis.
        """
        if ellipsis:
            return searches[0] in context or searches[-1] in context
        else:
            return self._find_index(context, searches) and True

    def _find_index(self, ctxt: Union[List[str], Words], searches: List,
                    start: int = 0) -> Union[Tuple[int, int], bool]:
        """Return the position of the start and end of a match of
        search_words list in context. If no match is made, return -1 in both
        tuple values.

        Procedure: If the first word of the searches is matched, start from
        that. While there are items in the search word list, see if the next
        item (that has content) in the context matches the next item in the
        search words list. """
        if not settings.sensitive_context_match:
            ctxt = [w.lower() for w in ctxt]
        else:
            ctxt = [str(w) for w in ctxt]

        if searches[0] not in ctxt[start:]:
            return False

        context_start = ctxt[start:].index(searches[0]) + start
        ctxt_index = context_start
        search_index = 0

        if ctxt_index is not -1:
            while len(searches) > search_index:
                try:
                    # We only match non-empty Word objects. This makes it
                    # match across non-text macros.
                    if ctxt[ctxt_index]:
                        if ctxt[ctxt_index] == searches[search_index]:
                            search_index += 1
                        else:
                            return self._find_index(ctxt, searches, ctxt_index)
                    ctxt_index += 1

                except IndexError:
                    # If there is an index error in the context lookup,
                    # the list has ended, so there is not full match.
                    return False

            # We +1 the last index to make it useable in a list slice
            return context_start, ctxt_index
        return False

    def _define_search_words(self, edtext: Words) -> Tuple[List, bool]:
        """
        From the Words that make up the edtext element, determine the search
        words based on either (1) the content of the lemma element in the
        apparatus note or (2) the content of the critical note.

        :return: Cleaned list of search words in lower case if we have a case
            insensitive search (not Words, but their .get_text())
        """
        # The apparatus note is the first item in app_entries of last Word
        app_note = edtext[-1].app_list.pop()
        lemma_pos = app_note.cont.find(r'\lemma')
        if lemma_pos is not -1:
            start = lemma_pos + len(r'\lemma')
            end = start + len(Brackets(app_note.cont, start=start))
            # Content excluding the brackets
            lemma_content = app_note.cont[start + 1:end - 1]
        else:
            lemma_content = ''

        if lemma_content:
            settings_pat = '|'.join([pat for pat in settings.ellipsis_patterns])
            ellipsis_pat = re.compile('(' + settings_pat + ')')
            ellipsis_search = re.search(ellipsis_pat, lemma_content)
            if ellipsis_search:
                spos = ellipsis_search.span()[0]
                epos = ellipsis_search.span()[1]
                lemma_word_list = (Tokenizer(lemma_content[:spos]).wordlist +
                                   Tokenizer(lemma_content[epos:]).wordlist)
                ellipsis = True
            else:
                lemma_word_list = Tokenizer(lemma_content).wordlist
                ellipsis = False

            if ellipsis:
                # Covers ellipsis lemma.
                content = ([lemma_word_list[0].get_text()] +
                           [lemma_word_list[-1].get_text()])
            elif len(lemma_word_list) == 1:
                # Covers single word lemma
                content = [lemma_word_list[0].get_text()]
            elif len(lemma_word_list) > 1:
                # Covers multiword lemma
                content = lemma_word_list.clean()
            else:
                content = []
                ellipsis = False
        else:
            content = edtext.clean()
            ellipsis = False
        if not settings.sensitive_context_match:
            content = [w.lower() for w in content]
        return content, ellipsis
