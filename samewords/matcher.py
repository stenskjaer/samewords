import regex
from warnings import warn

from samewords.tokenize import (
    Words,
    Registry,
    Word,
    Tokenizer,
    Macro,
    Element,
    LatexSyntaxError,
)
from samewords.brackets import Brackets
from samewords.settings import settings
from samewords.test import temp_settings

from typing import List, Tuple, Union


class Matcher:
    """
    Receives a wordlist and a registry and returns the wordlist annotated
    with samewords.
    """

    def __init__(self, words: Words, registry: Registry) -> None:
        self.words = words
        self.registry = registry

    def annotate(self, registry: Registry = None) -> Words:
        """
        Given a registry, determine whether there is a context match of
        the edtext lemma content for each entry and annotate accordingly.
        """
        if not registry:
            registry = self.registry

        for entry in registry:
            # Get data points for phrase and its start and end
            edtext_start = entry["data"][0]
            edtext_end = entry["data"][1] + 1
            edtext_lvl = entry["lvl"] + 1  # Reledmac 1-indexes the levels.
            edtext = self.words[edtext_start:edtext_end]

            # Identify search words and ellipsis
            search_ws, ellipsis = self._define_search_words(edtext)

            if ellipsis:
                # If we have a lemma note with ellipsis, we need to establish
                # context for both ellipsis elements (which may be nested
                # inside the edtext).
                ell_sidx = edtext.index(search_ws[0], default=0) + edtext_start
                ell_eidx = edtext.rindex(search_ws[1], default=0) + edtext_start

                el1_ctxt = self._get_contexts(self.words, ell_sidx)
                el2_ctxt = self._get_contexts(self.words, ell_eidx)
                contexts = el1_ctxt + el2_ctxt
            else:
                # Establish the context
                ctxt_before = self._get_context_before(self.words, edtext_start)
                ctxt_after = self._get_context_after(self.words, edtext_end)
                contexts = [w.get_text() for w in ctxt_before] + [
                    w.get_text() for w in ctxt_after
                ]

            # Is there a match in either context?
            if search_ws and self._in_context(contexts, search_ws, ellipsis):

                # Annotate the edtext
                # -------------------
                if ellipsis:
                    sidx = edtext.index(search_ws[0], default=0)
                    eidx = edtext.rindex(search_ws[1], default=0)
                    if self._in_context(el1_ctxt, search_ws[0:1], ellipsis):
                        self._add_sameword(edtext[sidx : sidx + 1], edtext_lvl)
                    if self._in_context(el2_ctxt, search_ws[-1:], ellipsis):
                        self._add_sameword(edtext[eidx : eidx + 1], edtext_lvl)
                else:
                    try:
                        with temp_settings({"sensitive_context_match": False}):
                            sidx, eidx = self._find_index(edtext, search_ws)
                    except TypeError:
                        raise ValueError(
                            "Looks like edtext and lemma content "
                            "don't match in "
                            "'{}'".format(edtext.write())
                        )

                    self._process_annotation(edtext, sidx, eidx, edtext_lvl)

                # Annotate the lemma if relevant
                # ------------------
                if r"\lemma" in edtext[-1].ann_apps[-1].cont:
                    # get the relevant app Element
                    app_note = edtext[-1].ann_apps[-1]
                    # split up the apparatus note into before, lem, after
                    s, e = self._find_lemma_pos(app_note)
                    if ellipsis:
                        # Tokenize the lemma words and ellipsis
                        # Annotate the lemma word where the context matches
                        # We want to annotate words even though they may not
                        # be first or last index in tokenized text. So we get
                        #  the indexes of those (list comp `idxs`) and then
                        # use those to index into the tokenized list in
                        # replacing.
                        lemma = self._find_ellipsis_words(app_note.cont[s:e])
                        idxs = [i for i, w in enumerate(lemma) if w.content]
                        if self._in_context(el1_ctxt, search_ws[0:1], ellipsis):
                            lemma[idxs[0]] = self._add_sameword(
                                lemma[idxs[0] : idxs[0] + 1], level=0
                            )[0]
                        if self._in_context(el2_ctxt, search_ws[-1:], ellipsis):
                            lemma[idxs[-1]] = self._add_sameword(
                                lemma[idxs[-1] : idxs[-1] + 1], level=0
                            )[0]

                    else:
                        lemma = Tokenizer(app_note.cont[s:e]).wordlist
                        lemma = self._process_annotation(lemma, 0, len(lemma), 0)

                    # patch app note up again with new lemma content
                    bef = app_note.cont[:s]
                    after = app_note.cont[e:]
                    new = bef + lemma.write() + after
                    # update the app note Element with the new content
                    edtext[-1].update_element(app_note, new)

                # Then annotate the contexts
                # ------------------------------
                if ellipsis:
                    for pos, word in zip([ell_sidx, ell_eidx], search_ws):
                        ctxt = self._get_context_before(
                            self.words, pos
                        ) + self._get_context_after(self.words, pos + 1)
                        if self._in_context(ctxt, [word], ellipsis):
                            self._annotate_context(ctxt, [word])
                else:
                    for ctxt in [ctxt_before, ctxt_after]:
                        self._annotate_context(ctxt, search_ws)

        return self.words

    def update(self) -> Words:
        """
        Given a registry, find all edtext elements that contain a `\sameword{}`
        annotation and check whether it is still correct. If not, update the
        annotation.
        """
        self.cleanup()
        self.annotate()
        return self.words

    def cleanup(self, wordlist: Words = None) -> Words:
        """Given a Words list, remove all sameword annotations."""
        if not wordlist:
            wordlist = self.words

        for val, word in enumerate(wordlist):
            if word.has_sameword:
                # Remove the macro itself.
                for i in [
                    v for v, m in enumerate(word.macros) if m.name == "\\sameword"
                ]:
                    close_idx = val + word.macros[i].to_closing
                    word.pop_macro(i)
                    wordlist[close_idx].pop_suffix()

                # Clean the app note's `\lemma{}` if there is any.
                for i in [
                    v
                    for v, a in enumerate(word.clean_apps)
                    if regex.search(r"\\lemma", a.cont)
                ]:
                    # get the relevant app Element
                    app_note = word.clean_apps[i]
                    # split up the apparatus note into before, lem, and after
                    s, e = self._find_lemma_pos(app_note)
                    if s == e:
                        # empty lemma
                        break
                    el_words = self._find_ellipsis_words(app_note.cont[s:e])
                    if el_words:
                        # Tokenize the lemma words and ellipsis
                        lem_words = el_words
                    else:
                        lem_words = Tokenizer(app_note.cont[s:e]).wordlist
                    lem_words = self.cleanup(lem_words)
                    # patch app note up again with new lemma content
                    bef = app_note.cont[:s]
                    after = app_note.cont[e:]
                    new = bef + lem_words.write() + after
                    # update the app note Element with the new content
                    word.update_element(app_note, new)
        return wordlist

    def validate(self) -> Union[Words, LatexSyntaxError]:
        for entry in self.registry:
            text = self.words[entry["data"][0] : entry["data"][1] + 1].write()
            s = 0
            pos = 0
            while pos < len(text):
                c = text[pos]
                if c == "{":
                    s += 1
                elif c == "}":
                    s -= 1
                pos += 1
            if s != 0:
                raise LatexSyntaxError(
                    "There are unbalanced parentheses in the following "
                    "string: \n" + text
                )
        return self

    def _get_contexts(self, words: Words, pivot: int) -> List:
        l1 = [w.get_text() for w in self._get_context_before(words, pivot)]
        l2 = [w.get_text() for w in self._get_context_after(words, pivot + 1)]
        return l1 + l2

    def _get_context_after(self, complete: Words, boundary: int) -> Words:
        distance = settings["context_distance"]
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
        distance = settings["context_distance"]
        end = boundary
        start = end
        count = 0
        while count < distance and start >= 0:
            w: Word = complete[start]
            start -= 1
            if w.content:
                count += 1
        if start == -1:
            return complete[:end]
        return complete[start:end]

    def _annotate_context(self, context: Words, searches: List) -> None:
        """In the context every match for a search word should be annotated
        when we annotate single words to get the counting right. If we are in
        a multiword setting, annotate all continous stretches of the search
        words."""
        if settings["multiword"] is False:
            for search in searches:
                indices = [
                    i
                    for i, c in enumerate(self._apply_sensitivity(context))
                    if c == search
                ]
                for idx in indices:
                    self._add_sameword(context[idx : idx + 1], level=0)
        else:
            indices = self._find_index(context, searches)
            if indices:
                while True:
                    start = indices[0]
                    end = indices[1]
                    self._process_annotation(context, start, end, 0)
                    new_indices = self._find_index(context, searches, start=end)
                    if new_indices:
                        indices = new_indices
                    else:
                        break

    def _process_annotation(
        self, part: Words, start: int, end: int, level: int
    ) -> Words:
        """Given a chunk of text, this will either annotate an indicated part
        of the chunk with a multiword or single word sameword annotations. """
        multi_parse_error = False
        if settings["multiword"] is True:
            old = part[start:end]
            self._add_sameword(part[start:end], level)
        else:
            for idx in range(start, end):
                if part[idx].content:
                    self._add_sameword(part[idx : idx + 1], level)
        return part

    def _add_sameword(self, part: Words, level: int) -> Words:
        """
        Wrap the `part` of words in a sameword macro with level indication,
        depending on some circumstances. If it is already wrapped in its
        entirety, we only update the sameword macro if necessary. If the
        level of an existing wrap is the same as the current, no change is
        made, otherwise that is updated.
        """
        if len([s for s in part if s.content]) == 0:
            warn(
                "There is an edtext element without any content that I think "
                "should be annotated. This may result in incorrect sameword "
                "numbering. The problem occurs in this section:\n" + part.write()
            )
            return part

        word: Word = part[0]

        # Should we handle the lemma level?
        if level is not 0:
            this_lvl = level
        else:
            this_lvl = ""

        # Are there any macros on the word that may create overlapping
        # problems? Figure out if any of them end before this \sameword{} is
        # supposed to end.
        short_idxs = [
            i
            for i, _ in enumerate(word.macros)
            if word.macros[i].to_closing < len(part) - 1
        ]
        try:
            # We take the first because it will be the lowest pos.
            short_idx = short_idxs[0]
        except IndexError:
            short_idx = -1

        # Is the phrase wrapped in a \sameword{}?
        sw_wrap = None
        lvl_match = None
        pat = regex.compile(r"(\\sameword)([^{]+)?")
        sw_idxs = [
            i for i, val in enumerate(word.macros) if regex.search(pat, val.full())
        ]
        try:
            sw_idx = sw_idxs[0]
        except IndexError:
            sw_idx = -1

        # If the first word is wrapped in a `\sameword{}`, and it is equal in
        #  length to the current chunk, then this chunk is already wrapped in
        #  its entirety, and should not be rewrapped. In that case we update
        # the wrap data.
        if sw_idx is not -1 and word.macros[sw_idx].to_closing == len(part) - 1:
            sw_match = regex.search(pat, word.macros[sw_idx].full())
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
                    lvl_set = set([int(i) for i in lvl_match.split(",")] + [this_lvl])
                    this_lvl = ",".join([str(i) for i in lvl_set])
                else:
                    # If lemma level of current annotation is None, keep the
                    # existing level argument.
                    this_lvl = lvl_match
            if this_lvl:
                this_lvl = "[" + str(this_lvl) + "]"
            sw_macro = Macro(r"\sameword" + this_lvl + "{")
            word.update_macro(sw_macro, sw_idx)

        # Otherwise, build the macro and put correctly into first word's macros.
        else:
            if this_lvl:
                sw_macro = Macro(r"\sameword[" + str(this_lvl) + "]{")
            else:
                sw_macro = Macro(r"\sameword{")

            # Does the word have a macro index that we need to take over by
            # the \sameword to put it before that macro?
            if short_idx is not -1:
                word.add_macro(sw_macro, short_idx)
            # Else, does the word already have a sameword wrap? If it is
            # shorter than the current chunk/part then the current macro should
            # go outside (by taking over its index and pushing that one in).
            elif sw_idx is not -1 and word.macros[sw_idx].to_closing < len(part) - 1:
                word.add_macro(sw_macro, sw_idx)
            # Otherwise, put it at the end of macros (making it the innermost).
            else:
                word.add_macro(sw_macro)

            # Add closing bracket to last word. If we have a multiword
            # wrapping, and the last word has both and opening and closing
            # edtext, then it contains an edtext that is nested inside the
            # current multiword wrap, and we therefore put the closing after
            # that.
            if len(part) > 1 and part[-1].edtext_start and part[-1].edtext_end:
                part[-1].append_suffix("}", after_clean_apps=True)
            else:
                part[-1].append_suffix("}")
            # And register its distance.
            word.close_macro(len(part) - 1)

        # Flip the sameword switch
        word.has_sameword = True

        # Update the first word
        part[0] = word
        return part

    def _apply_sensitivity(self, input_list: Union[List[str], Words]) -> List:
        if not settings["sensitive_context_match"]:
            return [w.lower() for w in input_list]
        return [str(w) for w in input_list]

    def _in_context(
        self, context: Union[List[str], Words], searches: List, ellipsis: bool
    ) -> bool:
        """Determine whether there is a match, either of a one- or multiword
        sequence or the first or last word in the sequence, in case it is an
        ellipsis.
        """
        context = self._apply_sensitivity(context)
        if ellipsis:
            return searches[0] in context or searches[-1] in context
        else:
            return self._find_index(context, searches) and True

    def _find_index(
        self, context: Union[List[str], Words], searches: List, start: int = 0
    ) -> Union[Tuple[int, int], bool]:
        """Return the position of the start and end of a match of
        search_words list in context. If no match is made, return -1 in both
        tuple values.

        Procedure: If the first word of the searches is matched, start from
        that. While there are items in the search word list, see if the next
        item (that has content) in the context matches the next item in the
        search words list. """
        context = self._apply_sensitivity(context)
        searches = self._apply_sensitivity(searches)

        if searches[0] not in context[start:]:
            return False

        context_start = context[start:].index(searches[0]) + start
        ctxt_index = context_start
        search_index = 0

        if ctxt_index is not -1:
            while len(searches) > search_index:
                try:
                    # We only match non-empty Word objects. This makes it
                    # match across non-text macros.
                    if context[ctxt_index]:
                        if context[ctxt_index] == searches[search_index]:
                            search_index += 1
                        else:
                            return self._find_index(context, searches, start=ctxt_index)
                    ctxt_index += 1

                except IndexError:
                    # If there is an index error in the context lookup,
                    # the list has ended, so there is not full match.
                    return False

            return context_start, ctxt_index
        return False

    def _find_lemma_pos(self, app_note: Element) -> Tuple[int, int]:
        """Given an apparatus note Element return the start and end index of
        the `\lemma{}` macro and return -1 for both start and end if it's not
        present. Before returning a positive result, the offset from the
        brackets is included. """
        lemma_pos = app_note.cont.find(r"\lemma")
        if lemma_pos is not -1:
            start = lemma_pos + len(r"\lemma")
            end = start + len(Brackets(app_note.cont, start=start))
            return start + 1, end - 1
        else:
            return -1, -1

    def _find_ellipsis_words(self, input_string: str) -> Words:
        """Determine whether input string has lemma ellipsis pattern and
        return the preceding and following word as elements in Words object.
        If there is no ellipsis pattern, return an empty Words list. """
        settings_pat = "|".join([pat for pat in settings["ellipsis_patterns"]])
        ellipsis_pat = regex.compile("(" + settings_pat + ")")
        ellipsis_search = regex.search(ellipsis_pat, input_string)
        if ellipsis_search:
            spos = ellipsis_search.span()[0]
            epos = ellipsis_search.span()[1]
            return (
                Tokenizer(input_string[:spos]).wordlist
                + Tokenizer(input_string[spos:epos]).wordlist
                + Tokenizer(input_string[epos:]).wordlist
            )
        return Words()

    def _define_search_words(self, edtext: Words) -> Tuple[List, bool]:
        """
        From the Words that make up the edtext element, determine the search
        words based on either (1) the content of the lemma element in the
        apparatus note or (2) the content of the critical note.

        When the apparatus notes are analyzed (the .clean_apps attribute)
        they are moved into the .ann_apps attribute. This means that an app
        element can never occur in both attributes (as that would result in
        duplicate entries of the app in printing)

        :return:
        """
        # The apparatus note is the first item in app_entries of last Word
        app_note = edtext[-1].clean_apps.pop()
        start, end = self._find_lemma_pos(app_note)
        if start is not -1:
            # Content excluding the brackets
            lemma_content = app_note.cont[start:end]
        else:
            lemma_content = ""

        if lemma_content:
            tokens = self._find_ellipsis_words(lemma_content)
            if tokens:
                ellipsis = True
            else:
                tokens = Tokenizer(lemma_content).wordlist
                ellipsis = False
            lem_wl = Words([w for w in tokens if w.content])
            if ellipsis:
                # Covers ellipsis lemma.
                content = [lem_wl[0].get_text()] + [lem_wl[-1].get_text()]
            elif len(lem_wl) == 1:
                # Covers single word lemma
                content = [lem_wl[0].get_text()]
            elif len(lem_wl) > 1:
                # Covers multiword lemma
                content = lem_wl.clean()
            else:
                content = []
                ellipsis = False
        else:
            content = edtext.clean()
            ellipsis = False
        if not settings["sensitive_context_match"]:
            content = [w.lower() for w in content]
        edtext[-1].ann_apps.append(app_note)
        return content, ellipsis
