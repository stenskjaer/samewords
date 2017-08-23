#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identify and annotate potentially ambiguous words in a string.
"""

import re
from typing import Iterable, List, Union, Tuple

from samewords import settings

# Type aliases
ContextList = List[List[str]]


class TextSegment(list):
    """
    A chunk of text. Can be anything from a whole paragraph to a short expression. Contains
    list of normal string and CritText objects.
    """

    def __init__(self, input_string: str) -> None:
        list.__init__(self, self.content_split(input_string))

    def content_split(self, search_string: str, return_list: List[str] = list(),
                      first: bool = True) -> List[str]:
        """
        Split the input `search_string` into list demarcated by `\edtext{}`-items.

        :param search_string: The input string.
        :param return_list: The list of text objects that should be returned.
        :param first: Indicate whether this is the first iteration, used in recursive processing.
        :return: List.
        """
        if first:
            return_list = []

        if r'\edtext' in search_string:
            appnote_start = search_string.find(r'\edtext')
            maintext_note_length = len(Macro(search_string[appnote_start:]).complete_macro())
            crit_note_length = Brackets(search_string,
                                        start=appnote_start + maintext_note_length).length
            appnote_end = appnote_start + maintext_note_length + crit_note_length

            if appnote_start > 0:
                return_list.append(search_string[:appnote_start])
            return_list.append(CritText(search_string[appnote_start:appnote_end]))
            return self.content_split(search_string[appnote_end:], return_list, first=False)

        else:
            if search_string is not '':
                return_list.append(search_string)
            return return_list

    def to_string(self) -> str:
        return ''.join(self)


class CritText(str):
    """
    A critical apparatus note.

    It takes a text segment containing exactly one critical text node like so: "\edtext{
    maintext}{critical text}". If the second argument contains a `\lemma`, that is used for
    determining the search words of the objects.
    """

    def __init__(self, input_string: str) -> None:
        str.__init__(input_string)
        self.content = input_string
        self.maintext_note = Brackets(self.content, macro=r'\edtext').content
        self.critical_note = Brackets(
            self.content, start=Brackets(self.content, macro=r'\edtext').length).content
        self.has_lemma = True if self.critical_note.find(r'\lemma') is not -1 else False
        self.lemma_content = self.get_lemma_content()
        self.dotted_lemma = False
        self.search_words = self.define_search_words()
        self.lemma_level = 1
        self.context_before: List[List[str]]
        self.context_after: List[List[str]]

    def define_search_words(self) -> List[str]:
        """
        From the lemma content, define which type of lemma we have and return appropriate list.

        :return: List of search words.
        """
        def add_ellipses(patterns: List[str]) -> str:
            return ''.join(['|({})'.format(pat) for pat in patterns])

        if self.has_lemma:
            lemma_word_list = Words(self.lemma_content).list
            ellipsis = re.compile(r'(\\l?dots({})?)' + add_ellipses(settings.ellipsis_patterns))
            if re.search(ellipsis, self.lemma_content):
                # Covers ldots lemma. We use the dots variable to identify first and last
                # word in dots lemmas.
                search_words = [lemma_word_list[0]] + [lemma_word_list[-1]]
                self.dotted_lemma = True
            elif len(lemma_word_list) == 1:
                # Covers single word lemma
                search_words = [self.lemma_content]
            elif len(lemma_word_list) > 1:
                # Covers multiword lemma. We join them to one "search_word" as we look for
                # that specific phrase in proximity, not just any of its containing words.
                search_words = [' '.join(lemma_word_list)]
            else:
                search_words = []
        else:
            return [Words(self.maintext_note).to_string()]
        return search_words

    def get_lemma_content(self):
        """Isolate the content of the `\lemma{}` macro in the critical note."""
        if self.has_lemma:
            return Brackets(self.critical_note, macro=r'\lemma').content
        else:
            return None

    def assemble(self, maintext=None, critical=None):
        """Wrap maintext_note and critical_note in `\edtext{}{}` macro.
        """
        if maintext is None:
            maintext = self.maintext_note
        if critical is None:
            critical = self.critical_note
        self.content = r'\edtext{' + maintext + '}{' + critical + '}'
        return CritText(self.content)

    def replace_in_maintext_note(self, replace_word: str, replace_string: str = None,
                                 lemma_level: int = 1) -> str:
        """
        Replace all instances of `replace_word` in a apparatus note (full `\edtext{}{}`) and return
        the updated string.

        We instantiate self.maintext_note or `replace_string` (if given) as TextSegment,
        thus splitting it into segments of critical notes and regular text. That list is
        iterated, wrapping any match of `replace_word` as we go along.

        Updates self.maintext_note and return the updated self.content or returns the updated
        `replace_string` if given.

        The possibility of passing `replace_string` is required for recursive calls in nested
        edtext elements.

        :param replace_word: The word to be replaced.
        :param replace_string: A string to wrap replacement words (optional).
        :param lemma_level: The level from which the lemma refers to the word to be `replace_word`.
        :return Updated replace_string or content of self.
        """

        return_string = ''
        if replace_string is not None:
            edtext_content_list = TextSegment(replace_string)
        else:
            edtext_content_list = TextSegment(self.maintext_note)

        if self.dotted_lemma:
            # We have a ldots lemma, so only replace at the beginning and end of the edtext element.
            if replace_word == self.search_words[0]:
                edtext_content_list[0] = self.replace_first_maintext_word(
                    replace_word=replace_word,
                    replace_string=edtext_content_list[0],
                    lemma_level=lemma_level)
            elif replace_word == self.search_words[1]:
                edtext_content_list[-1] = self.replace_last_maintext_word(
                    replace_word=replace_word,
                    replace_string=edtext_content_list[-1],
                    lemma_level=lemma_level)
            return_string = ''.join(edtext_content_list)

        else:
            for pivot_index, edtext_content in enumerate(edtext_content_list):

                if isinstance(edtext_content, CritText):
                    # If the item is a critical note, replace inside it.
                    maintext = self.replace_in_maintext_note(
                        replace_word, lemma_level=lemma_level,
                        replace_string=edtext_content.maintext_note)
                    edtext_content_list[pivot_index] = self.assemble(
                        maintext=maintext, critical=edtext_content.critical_note)

                else:
                    edtext_content_list[pivot_index] = replace_in_string(
                        replace_word, edtext_content, lemma_level)

                return_string += edtext_content_list[pivot_index]

        if replace_string is not None:
            return return_string
        else:
            # Update the maintext parameter and update self.content with assemble()
            self.maintext_note = return_string
            return self.assemble()

    def replace_last_maintext_word(self, replace_string: str, replace_word: str,
                                   lemma_level: int = 1) -> str:
        """
        Replace only on the very last maintext word of `replace_string` (if it matches).

        :return: The updated `replace_string`.
        """
        segments = TextSegment(replace_string)
        self.dotted_lemma = False
        segment = segments[-1]
        if isinstance(segment, CritText):
            maintext = self.replace_last_maintext_word(segment.maintext_note, replace_word,
                                                       lemma_level)
            segments[-1] = segment.assemble(maintext=maintext)
        else:
            previous = ' '.join(segment.split(' ')[:-1])
            last = segment.split(' ')[-1]
            updated_last = self.replace_in_maintext_note(replace_word, last, lemma_level)
            segments[-1] = previous + ' ' + updated_last

        return segments.to_string()

    def replace_first_maintext_word(self, replace_string: str, replace_word: str,
                                    lemma_level: int =1) -> str:
        """
        Replace only the very first maintext word of `replace_string` (if it matches).
        """
        segments = TextSegment(replace_string)
        self.dotted_lemma = False
        segment = segments[0]
        if isinstance(segment, CritText):
            maintext = self.replace_first_maintext_word(segment.maintext_note, replace_word,
                                                        lemma_level)
            segments[0] = segment.assemble(maintext=maintext)
        else:
            first = segment.split(' ')[0]
            rest = ' '.join(segment.split(' ')[1:])
            updated_first = self.replace_in_maintext_note(replace_word, first, lemma_level)
            segments[0] = updated_first + ' ' + rest

        return segments.to_string()

    def replace_in_critical_note(self, replace_word: str) -> str:
        """
        Update content of critical note by wrapping possible match words.
        """
        lemma_content = Brackets(self.critical_note, macro=r'\lemma').content

        # Store everything up to start of lemma content.
        position = self.critical_note.find(r'{') + 1
        return_string = self.critical_note[:position]

        # Replace the content and put into return list.
        return_string += replace_in_string(replace_word, lemma_content, lemma_level=0)
        position += len(lemma_content)

        # Add the following app note, where nothing should be changed, and return it
        return_string += self.critical_note[position:]

        # Update the maintext parameter and update self.content with assemble()
        self.critical_note = return_string
        return self.assemble()

    def replace_in_edtext_args(self, replace_word: str, lemma_level: int = 1) -> str:
        self.replace_in_maintext_note(replace_word, lemma_level=lemma_level)
        if self.has_lemma:
            self.replace_in_critical_note(replace_word)
        return self.content


class Context:
    """The context of a text segment in list of lists reflecting nesting level."""

    def __init__(self):
        self.before = []
        self.after = []

    def update(self, raw_before: TextSegment, raw_after: TextSegment,
               lemma_level: int = 1):
        """
        Build the surrounding context. If is a list of lists, list 0 contains context on lvl 1,
        list 1 contains context on lvl 2 etc.
        """
        prox_context_before = self.iter_proximate_words(raw_before, side='left')
        prox_context_after = self.iter_proximate_words(raw_after, side='right')

        try:
            self.before[lemma_level - 1] = prox_context_before
        except IndexError:
            self.before = self.before + [prox_context_before]
        try:
            self.after[lemma_level - 1] = prox_context_after
        except IndexError:
            self.after = self.after + [prox_context_after]

    def iter_proximate_words(self, input_list, index=0, word_count_sum=0, side='', length=15):
        """
        Get a suitable amount of items from input_list to serve the amount of proximity words
        defined by length.

        When the `side` is `left`, it is reversed before and after processing to start the
        counting from the end.

        :param input_list: The list to pull from
        :param index: The index from where the search should start.
        :param word_count_sum: Accumulative word counter for finding the right size chunk.
        :param side: Indicate whether we are searching left of the pivot. In that case, we reverse
            the list too.
        :param length: Amount of words required for the chunk.
        :return: List of at least length equal to the word count defined by `length` on each side
            of the pivot word (unless we are at the fringe of a string).
        """
        if side == 'left' and index == 0:
            # If we are on first iteration of left, reverse the input list.
            input_list = list(reversed(input_list))

        try:
            word_count_sum += len(Words(input_list[index]).list)
        except IndexError:
            pass

        if word_count_sum < length and index + 1 < len(input_list):
            return self.iter_proximate_words(input_list, index + 1, word_count_sum, side)
        else:
            if side == 'left':
                return list(reversed(input_list[:index + 1]))
            else:
                return input_list[:index + 1]


class Brackets:
    """Object describing the content and length of a LaTeX macro brackets.
    """

    def __init__(self, search_string, start: int = 0, macro: str = '') -> None:
        str.__init__(search_string)
        self.content = self.content(search_string, start, macro)
        self.length = self.length(start, macro)

    def length(self, position: int = 0, macro: str = '') -> int:
        """Calculate the length of the macro command.
        """
        start_position = position
        bracket_offset = 2
        if macro:
            position += len(macro)
        position += len(self.content)
        position += bracket_offset
        return position - start_position

    @staticmethod
    def content(search_string: str, position: int, macro: str) -> str:
        """Get the content of the macro and return it.
        """
        special_chars = r'\&%$#_{}~^'
        capture = ''

        if re.match('\n+\s+', search_string[position:]):
            position += len(re.match('\n+\s+', search_string[position:]).group(0))

        if macro:
            if search_string[position:position + len(macro)] == macro:
                position += len(macro)
            else:
                raise ValueError("The indicated macro, %s, did not occur at position %i."
                                 "Context: %s"
                                 % (macro, position, search_string[position:position + 20]))

        if search_string[position] == '{':
            stack = 1
            position += 1
        else:
            raise ValueError(
                "The first symbol of the match string must be an opening bracket ({). \n"
                "Context: %s" % search_string[position:position + 50])

        while stack > 0:
            try:
                symbol = search_string[position]
                if symbol == '{':
                    stack += 1
                elif symbol == '}':
                    stack -= 1
                elif symbol == '\\' and search_string[position + 1] in special_chars:
                    capture += symbol
                    symbol = search_string[position + 1]
                    position += 1
                capture += symbol
                position += 1
            except IndexError:
                raise ValueError("Unbalanced brackets. The provided string terminated before all "
                                 "brackets were closed.")
        return capture[:-1]


class Macro:
    """A full latex macro, identified from `start` to where the macro is completed.
    """

    def __init__(self, input_string: str, start: int = 0) -> None:
        self.input_string = input_string
        self.start = start
        self.has_opening = False
        self.name = self.identify_name()
        self.before_opening = self.before_opening()

    def __repr__(self) -> str:
        return self.before_opening

    def identify_name(self) -> str:
        return re.match(r'[^\s[{]+', self.input_string[self.start:]).group(0)

    def before_opening(self) -> str:
        opening = re.match(r'[^\s]+?{', self.input_string)
        if opening:
            self.has_opening = True
            return opening.group(0)[:-1]
        else:
            space_pos = -1
            if re.search(r'\s', self.input_string[self.start:]):
                space_pos = re.search(r'\s', self.input_string[self.start:]).start()
            return self.input_string[self.start:space_pos]

    def complete_macro(self) -> str:
        if self.has_opening:
            position = self.start + self.input_string[self.start:].find('{')
            return self.before_opening \
                + '{' + Brackets(self.input_string, start=position).content + '}'
        else:
            return self.before_opening

    def content(self) -> str:
        if self.has_opening:
            position = self.start + self.input_string[self.start:].find('{')
            return Brackets(self.input_string, start=position).content
        else:
            return ''


class Word(str):

    def __init__(self, input_string):
        str.__init__(self)
        self.content = input_string
        self.start = 0
        self.end = self.start + len(input_string)
        self.wrapped = False
        self.wrap_macro = ''

    def __iadd__(self, other):
        """Perform inplace addition by copying the current object to new and making addition."""
        old = self
        w = Word(self + other)
        w.start = old.start
        w.end = old.start + w.end
        w.wrapped = old.wrapped
        w.wrap_macro = old.wrap_macro
        return w

    def flatten(self, obj) -> Iterable[str]:
        """Return a flat list from an arbitrarily nested list of Word objects."""
        if isinstance(obj.content, list):
            for item in obj.content:
                yield from self.flatten(item)
        else:
            yield obj.content

    def to_string(self):
        return ' '.join(list(self.flatten(self)))


class Words:

    def __init__(self, input_string):
        self.input_string = input_string
        self.list = self.clean(input_string)

    def clean(self, search_string: str, global_offset: int = 0):

        if isinstance(search_string, CritText):
            search_string = search_string.maintext_note

        ignored_macros = settings.exclude_macros
        keep_macros = settings.include_macros

        ls = []
        position = 0
        word = None
        while position < len(search_string):

            if re.match('\w', search_string[position]):
                # If we match word character, store that word and start position, and bump to
                # following symbol.
                chunk = re.match('\w+', search_string[position:]).group(0)
                if word is not None:
                    position += len(word.content)
                    word += chunk
                    ls[-1] = word  # word is immutable. __iadd__ returns new object, so update list.
                    word.end += position + global_offset
                else:
                    word = Word(chunk)
                    ls.append(word)
                    word.start = position + global_offset
                    position += len(word.content)
                    word.end = position + global_offset
                continue

            if search_string[position] == '\\':
                # If symbol is macro
                macro = Macro(search_string[position:])
                if macro.name in ignored_macros:
                    position += len(macro.complete_macro())
                    if word:
                        word.end += position + global_offset
                    continue
                elif macro.name in keep_macros:
                    if word:
                        position += len(macro.complete_macro())
                        word += macro.complete_macro()
                        ls[-1] = word
                        word.end = position + global_offset
                    else:
                        word = Word(macro.complete_macro())
                        word.start = position + global_offset
                        position += len(macro.complete_macro())
                        word.end = position + global_offset
                        ls.append(word)
                    continue
                elif macro.name == '\\sameword':
                    offset_pos = position + global_offset + len(macro.before_opening + '{')
                    word = Word(self.clean(macro.content(), global_offset=offset_pos))
                    word.wrap_macro = macro.before_opening
                    word.start = position + global_offset
                    position += len(macro.complete_macro())
                    word.end = position + global_offset
                    ls.append(word)
                    continue
                else:
                    # macro call should not be registered in search string.
                    if word:
                        # If we are recording a word, store content of macro as part of word.
                        position += len(macro.complete_macro())
                        word += macro.content()
                        ls[-1] = word
                        word.end = position
                        continue
                    else:
                        position += len(macro.before_opening)

            if re.match('\W', search_string[position]):
                position += 1

            word = None
        return ls

    def to_string(self) -> str:
        """Return a flattened cleaned string of the Words object."""
        return ' '.join([i.to_string() for i in self.list])


def search_in_proximity(search_word: str, context_before: List[List[str]],
                        context_after: List[List[str]]) -> bool:
    """
    Check whether a search word is present in the one of two lists. The two input lists contain
    the context of the search word.

    We need to search for a regex demarcating the string with boundaries to make sure we don't
    just match a partial word ("so" matching "something"). We can't demarcate by whitespace,
    as that may not always be present.

    :param search_word: The word we look for.
    :param context_before: List of preceding context to be searched.
    :param context_after: List of following context to be searched.
    :return: Boolean.
    """
    def flatten_list(input_list: Union[str, list]) -> Iterable[str]:
        """Return a flat list from an arbitrarily nested list."""
        for item in input_list:
            if type(item) == list:
                yield from flatten_list(item)
            else:
                yield item

    contexts = flatten_list(context_before + context_after)

    for context_chunk in contexts:
        maintext_words = Words(context_chunk).to_string()
        search_word = Words(search_word).to_string()
        if re.search(r'(?<!\w)' + re.escape(search_word.casefold()) + '(?!\w)',
                     maintext_words.casefold()):
            return True
    return False


def replace_in_proximity(context_before_list: ContextList, context_after_list: ContextList,
                         search_word: str) -> Tuple[ContextList, ContextList]:
    """
    Replace a specified search word in two lists containing the text surrounding a chunk of text.

    This is used for replacing a word that is present in an `\edtext{}`-element and that is
    confirmed to be in the proximate context.

    The replacement is only done on the proximity of the pivot element.

    :param search_word: The word to be replaced in surrounding text.
    :param context_after_list: The context list contaning the preceding content.
    :param context_before_list: The context list contaning the following content.
    :return: The two updated lists where samewords of the search word are marked.
    """

    def replace_in_context_list(context_list: ContextList, word: str) -> ContextList:
        for item_index, context_item in enumerate(context_list):
            for index, chunk in enumerate(context_item):
                if isinstance(chunk, CritText):
                    chunk = chunk.replace_in_maintext_note(word, lemma_level=0)
                else:
                    chunk = replace_in_string(word, chunk)
                context_item[index] = chunk
            context_list[item_index] = context_item
        return context_list

    left = replace_in_context_list(context_before_list, search_word)
    right = replace_in_context_list(context_after_list, search_word)

    return left, right


def replace_in_string(replace_word: str, replace_string: str, lemma_level: int = 0) -> str:
    """
    Recursively replace the search word in the search string with a version that is wrapped in
    sameword. This is designed to handle replacement of multiword phrases in the string too. The
    wrapping is done intelligently so that what is already wrapped is not double wrapped,
    and lemma levels are incorporated.

    :param replace_word: the word that should be wrapped
    :param replace_string: The string in which the replacement should be done.
    :param lemma_level: The lemma level, if applicable.
    :return: Updated or unchanged string.
    """
    def check_list_match(pattern_list: List[str], replace_list: List[Word],
                         return_list: List[str] = list(), first: bool = True) -> List[Word]:
        """Check whether a word string in `pattern_list` (search phrase) is matched in
        `replace_list`.

        Check whether first item of `pattern_list` is contained in first item of
        `replace_list`. If it does, move on to next item in `pattern_list` until it is exhausted.
        This way it matches whole string of words specified in `pattern_list` in `replace_list`.

        When the caller of this function iterates through the `replace_list`, it is incrementally
        checked in full. We want to keep the formatting of the search list, so items from that
        are returned in order as they are.

        During matching we need to maintain whitespace in the list being matched (`replace_list`).
        So when there is any content in the return_list (a match has started), and a match fails
        because the replace_list content is whitespace, add that to the return_list.

        :param pattern_list: List of search words to be matched in `replace_list`.
        :param replace_list: List of words to be matched.
        :param return_list: The results to be returned, built successively in recursive calls.
        :param first: Indicate whether we are at the first iteration on a recursive stack.
        :return List of items from `replace_list` that match items in `pattern_list`.

        """
        if first:
            return_list = []
        try:
            word = replace_list[0]
            # If first item of match list is in word item (first item in sublist) of
            # replace_list, register the start and end of that word in return_list.

            if isinstance(word.content, list):
                match = word.to_string()
            else:
                match = word.content

            if re.search(r'(?<!\w)' + re.escape(pattern_list[0].casefold()) + '(?!\w)',
                         match.casefold()):
                return_list.append(word)
                return check_list_match(pattern_list[1:], replace_list[1:],
                                        return_list, first=False)
        except IndexError:
            return return_list

    def make_replacements(search_list: List[str], word_list: List[Word], orig_string: str,
                          wrap_item: Word = None, context: List[Word] = None,
                          offset: int = 0) -> str:
        """
        Directing function for replacement.

        This analyses a string of `Word` objects (returned by the `Words().list` parameter).
        Since the clean function of `Words` returns a potentially nested list (sameword
        annotations are processed as a nested list of their content), this handles `Word().content`
        as either `str` or `list`.

        :param search_list: List of `str` objects providing match patterns for string matching.
        :param word_list: List of `Word` objects representing a cleaned version of `orig_string`.
        :param orig_string: The original form of the string with the content we want to replace.
        :param wrap_item: On recursion this provides context for wrap positions.
        :param context: On recursion this provides the parent context list.
        :param offset: Used for updated position index on multiple matches on same string.
        :return: Updated string containing sameword annotations.
        """
        if not word_list:
            # Word list is empty and we made no matches. Return the original string.
            return orig_string
        if isinstance(word_list[0].content, str):
            # The word contains a non-wrapped string that we can match.
            matches = check_list_match(search_list, word_list)
            if matches:

                start = matches[0].start + offset
                end = matches[-1].end + offset

                if wrap_item:
                    # Create return string and copy all up to start
                    updated = orig_string[:wrap_item.start + offset]
                else:
                    updated = orig_string[:start]

                phrase = orig_string[start:end]
                len_before_wrap = len(phrase)
                wrapped_phrase = wrap_phrase(phrase, lemma_level=lemma_level, wrap=wrap_item)
                len_after_wrap = len(wrapped_phrase)
                offset += len_after_wrap - len_before_wrap

                # wrap the phrase (handles wrapped macro too)
                updated += wrapped_phrase

                if wrap_item:
                    updated += orig_string[wrap_item.end:]
                else:
                    updated += orig_string[end:]
                return make_replacements(search_list, word_list[1:], updated, offset=offset)
            else:
                if context:
                    # No match on this recursion level, so we continue from parent context.
                    return make_replacements(search_list, context[1:], orig_string,
                                             wrap_item=None, offset=offset)
                else:
                    return make_replacements(search_list, word_list[1:], orig_string,
                                             wrap_item=None, offset=offset)
        else:
            # The word contains a list of Word obj's that we must go through. Replace with
            # content as input list, the object as position context and the whole word_list for
            # context preservation when we continue after the recursion.
            return make_replacements(search_list, word_list[0].content, orig_string,
                                     wrap_item=word_list[0], context=word_list)

    unwrapped = False
    try:
        if replace_string[0] is '{' and replace_string[-1] is '}':
            replace_string = replace_string[1:-1]
            unwrapped = True
    except IndexError:
        # The input replacement string is empty, so just return with processing.
        return replace_string

    words_list = Words(replace_string).list
    search_words = replace_word.split(' ')
    if words_list:
        updated_replace_string = make_replacements(search_words, words_list, replace_string)
    else:
        updated_replace_string = replace_string

    if unwrapped:
        return '{' + updated_replace_string + '}'
    return updated_replace_string


def wrap_phrase(phrase: str, lemma_level: int = 0, wrap: Word = None) -> str:
    """
    Wrap the word or phrase in the appropriate \sameword{}-element.

    This means that if the word or phrase is already wrapped in a \sameword{}, it cannot be
    wrapped in another. If one or more words of a phrase are wrapped, it should wrap the whole
    phrase. It also needs to handle the conditions of lemma level numbering.

    :param wrap: `Word` object containg information on wrapping macro.
    :param phrase: the word or phrase that should be wrapped.
    :param lemma_level: the level of the lemma annotation. Default=0
    :return: The wrapped input phrase
    """

    # Should we handle the lemma level?
    if lemma_level is not 0:
        this_level = lemma_level
    else:
        this_level = ''

    # Is the phrase wrapped?
    sameword_wrap = None
    lvl_match = None
    if wrap:
        sw_match = re.match(r'(\\sameword)([^{]+)?', wrap.wrap_macro)
        sameword_wrap = sw_match.group(0)
        lvl_match = sw_match.group(2)

    if sameword_wrap:
        if lvl_match:
            # Peel of the wrapping brackets
            lvl_match = lvl_match[1:-1]
            # Wrap contains level indication
            if this_level:
                # If we have a lemma level here, combine with existing level argument.
                lvl_set = set([int(i) for i in lvl_match.split(',')] + [this_level])
                sameword_level = ','.join([str(i) for i in lvl_set])
                this_level = sameword_level
            else:
                # If lemma level of current annotation is None, keep the existing level argument.
                this_level = lvl_match
        if this_level:
            this_level = '[' + str(this_level) + ']'
        phrase = r'\sameword' + this_level + '{' + phrase + '}'
    else:
        if this_level:
            phrase = r'\sameword' + '[' + str(this_level) + ']' + '{' + phrase + '}'
        else:
            phrase = r'\sameword' + '{' + phrase + '}'
    return phrase


def critical_note_match_replace_samewords(text: str) -> str:
    """
    The main search and replace function.

    The included function `sub_processing` orchestrates the main process. The wrapper function
    passes a TextSegment object to the processing function. The TextSegment class segments the
    string into chunks of `\edtext{}`-elements (stored as CritText objects) and regular text. All
    CritText objects are processed by identifying whether any search words of the content in the
    critical note is present in the proximate context. When that is the case, we process the
    context along with the critical note itself. If the critical note contains any nested
    `\edtext{}` elements, we recurse to the innermost element and start from there.

    Search and replace in proximity works like this: Receive a list of lists. Each list in the
    list represents a lemma level: List 1 is the context of first edtext element, list 2 is the
    context of the contained edtext element etc.

    :param text: The string that should be processed.
    :return: The processed string with encoding of disambiguation.
    """

    def sub_processing(text_object, context=Context(), lemma_level=1):

        for pivot_index, segment in enumerate(text_object):

            if isinstance(segment, CritText):

                # Build the surrounding context. If is a list of lists. List 0 contains context
                # on lvl 1, list 1 contains context on lvl 2 etc.
                context.update(text_object[:pivot_index], text_object[pivot_index + 1:],
                               lemma_level)

                if r'\edtext' in segment.maintext_note:
                    # We have a nested apparatus note here, so before moving on, we process that.
                    lemma_level += 1
                    output = sub_processing(TextSegment(segment.maintext_note),
                                            context, lemma_level=lemma_level)
                    segment.maintext_note = output.to_string()
                    segment.content = segment.assemble()
                    lemma_level -= 1

                for search_word in segment.search_words:

                    if search_in_proximity(search_word, context.before, context.after):
                        # Update the proximate content.
                        context.before, context.after = replace_in_proximity(
                            context.before, context.after, search_word)

                        segment.replace_in_edtext_args(search_word, lemma_level=lemma_level)

                #  We update the pivot and surrounding material
                proximate_before = context.before.pop()
                proximate_after = context.after.pop()
                text_object[pivot_index - len(proximate_before):pivot_index] = proximate_before
                text_object[pivot_index] = CritText(segment.content)
                text_object[pivot_index+1:len(proximate_after) + pivot_index+1] = proximate_after

        return text_object

    result = sub_processing(TextSegment(text))

    return result.to_string()
