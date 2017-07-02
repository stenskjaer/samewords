#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identify and annotate potentially ambiguous words in a string.
"""

import re


class TextSegment(list):
    """
    A chunk of text. Can be anything from a whole paragraph to a short expression. Contains 
    list of normal string and CritText objects. 
    """

    def __init__(self, input_string: str) -> None:
        list.__init__(self, self.content_split(input_string))

    def content_split(self, search_string: str, return_list: list = list(),
                      first: bool = True) -> list:
        """
        Split the input `search_string` into list demarcated by `\edtext{}`-items.

        :param search_string: The input string.
        :param return_list: The list of text objects that should be returned.
        :param first: Indicate whether this is the first iteration, used in recursive processing.
        :return: List.
        """
        if first:
            return_list: list = []

        if r'\edtext' in search_string:
            appnote_start = search_string.find(r'\edtext')
            edtext_length = macro_expression_length(
                search_string, position=appnote_start, macro=r'\edtext')
            appnote_length = macro_expression_length(search_string, appnote_start + edtext_length)
            appnote_end = appnote_start + edtext_length + appnote_length

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
    """

    def __init__(self, input_string):
        str.__init__(input_string)
        self.content = input_string
        self.maintext_note = macro_expression_content(self.content, macro=r'\edtext')
        self.critical_note = macro_expression_content(
            self.content, position=macro_expression_length(self.content, macro=r'\edtext'))
        self.has_lemma = True if self.critical_note.find(r'\lemma') is not -1 else False
        self.lemma_content = self.get_lemma_content()
        self.dotted_lemma = False
        self.search_words = self.define_search_words()
        self.lemma_level = 1
        self.context_before = list()
        self.context_after = list()

    def define_search_words(self):
        """
        From the lemma content, define which type of lemma we have and return appropriate list.

        :return: List of search words.
        """
        # Determine lemma type. The `dots` variable is used for processing of ldots notes.
        if self.has_lemma:
            lemma_word_list = list_maintext_words(self.lemma_content)
            if re.search(r'\\l?dots({})?', self.lemma_content):
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
            return [self.maintext_note]
        return search_words

    def get_lemma_content(self):
        """Isolate the content of the `\lemma{}` macro in the critical note."""
        if self.has_lemma:
            return macro_expression_content(self.critical_note,
                                            position=len(r'\lemma'))
        else:
            return None

    def assemble(self, maintext=None, critical=None):
        """Wrap maintext_note and critical_note in `\edtext{}{}` macro. 
        """
        if not maintext:
            maintext = self.maintext_note
        if not critical:
            critical = self.critical_note
        self.content = r'\edtext{' + maintext + '}{' + critical + '}'
        return CritText(self.content)

    def replace_in_maintext_note(self, replace_word, replace_string=None, lemma_level=1):
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
        if replace_string:
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
            loop_string = ''
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

                loop_string += edtext_content_list[pivot_index]

            return_string += loop_string

        if replace_string:
            return return_string
        else:
            # Update the maintext parameter and update self.content with assemble()
            self.maintext_note = return_string
            return self.assemble()

    def replace_last_maintext_word(self, replace_string, replace_word, lemma_level=1):
        """
        Replace only on the very last maintext word of `replace_string` (if it matches).
        
        :return: The updated `replace_string`. 
        """
        segments = TextSegment(replace_string)
        self.dotted_lemma = False
        for index, segment in enumerate(segments):
            if index + 1 == len(segments):
                if isinstance(segment, CritText):
                    maintext = self.replace_last_maintext_word(segment.maintext_note, replace_word,
                                                               lemma_level)
                    segments[index] = segment.assemble(maintext=maintext)
                else:
                    previous = ' '.join(segment.split(' ')[:-1])
                    last = segment.split(' ')[-1]
                    updated_last = self.replace_in_maintext_note(replace_word, last, lemma_level)
                    segments[index] = previous + ' ' + updated_last

        return segments.to_string()

    def replace_first_maintext_word(self, replace_string: str, replace_word: str,
                                    lemma_level: int =1) -> str:
        """
        Replace only the very first maintext word of `replace_string` (if it matches).
        """
        segments = TextSegment(replace_string)
        self.dotted_lemma = False
        for index, segment in enumerate(segments):
            if index == 0:
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


    def replace_in_critical_note(self, replace_word, replace_string=None):
        """
        Update content of critical note by wrapping possible match words.
        """

        if replace_string:
            lemma_content = macro_expression_content(replace_string, position=len(r'\lemma'))
        else:
            lemma_content = macro_expression_content(self.critical_note, position=len(r'\lemma'))

        return_string = r'\lemma{'
        position = len(r'\lemma{')
        return_string += replace_in_string(replace_word, lemma_content, lemma_level=0)

        position += len(lemma_content)

        # Add the following app note, where nothing should be changed, and return it
        return_string += self.critical_note[position:]

        # Update the maintext parameter and update self.content with assemble()
        self.critical_note = return_string
        return self.assemble()

    def replace_in_edtext_args(self, replace_word, lemma_level=1):
        self.replace_in_maintext_note(replace_word, lemma_level=lemma_level)
        if self.has_lemma:
            self.replace_in_critical_note(replace_word)
        return self.content


class Context:
    """The context of a text segment in list of lists reflecting nesting level."""

    def __init__(self):
        self.before = []
        self.after = []

    def update(self, raw_before: TextSegment, raw_after: TextSegment, lemma_level=1):
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
        Get a suitable amount of items from input_list to serve 30 proximity words for analysis.

        When the `side` is `left`, it will return the list reversed thereby yielding the items 
        closest to the search start. 

        :param input_list: The list to pull from
        :param index: The index from where the search should start.
        :param word_count_sum: Accumulative word counter for finding the right size chunk.
        :param side: Indicate whether we are searching left of the pivot. In that case, we reverse 
            the list too.
        :param length: Amount of words required for the chunk.
        :return: List of at least 30 word on each side of the pivot word (less if we are at the end 
            of the string).
        """

        try:
            word_count_sum += len(list_maintext_words(input_list[index]))
        except IndexError:
            pass

        if side == 'left':
            if word_count_sum < length and index > 0:
                return self.iter_proximate_words(input_list, index - 1, word_count_sum, side)
            else:
                return input_list[index:]
        elif side == 'right':
            if word_count_sum < length and index + 1 < len(input_list):
                return self.iter_proximate_words(input_list, index + 1, word_count_sum, side)
            else:
                return input_list[:index + 1]


def macro_expression_content(search_string, position=0, opener='{', closer='}', capture_wrap=False,
                             macro=''):
    """Get the content of a latex expression that has been opened with "{" to any
    level of macro nesting until closing "}".

    This function expects the character at the starting position of the match string to be an 
    opening bracket and will complain if it is not. This means that it initializes the stack with 
    that opening bracket in the stack. When the stack is empty, we have reached the end of the 
    expression, and should return the string capture thus far. 

    :param search_string: The string to be processed.
    :param position: The starting position in the string [default: 0].
    :param opener: Symbol that opens bracket set [default='{'].
    :param closer: Symbol that closes bracket set [default='}'].
    :param capture_wrap: Capture the wrapping (outermost) brackets [default=False].
    :param macro: If this is given, the processing will skip that as first initial macro.
    :return: The string captured.
    """

    special_chars = r'\&%$#_{}~^'
    capture = ''

    if macro:
        position = len(macro)

    if search_string[position] == opener:
        stack = [opener]
        if capture_wrap:
            capture += search_string[position]
        position += 1
    else:
        raise ValueError("The first symbol of the match string must be an opening bracket ({). \n"
                         "Context: %s" % search_string[position:position + 50])

    while len(stack) > 0:
        try:
            symbol = search_string[position]
            if symbol == opener:
                stack.append(symbol)
            elif symbol == closer:
                stack.pop()
            elif symbol == '\\' and search_string[position + 1] in special_chars:
                capture += symbol
                symbol = search_string[position + 1]
                position += 1
            capture += symbol
            position += 1
        except IndexError:
            raise ValueError("Unbalanced brackets. The provided string terminated before all "
                             "brackets were closed.")
    if not capture_wrap:
        capture = capture[:-1]
    return capture


def macro_expression_length(search_string, position=0, opener='{', closer='}', macro=''):
    """Calculate length of macro expression.

    This function expects the character at the starting position of the match string to be an 
    opening bracket and will complain if it is not. Actually it just finds the position where 
    those two are balanced and returns that. 

    :param search_string: The string to be processed.
    :param position: The starting position in the string [default: 0].
    :param opener: The character that opens a bracket to be matched.
    :param closer: The character that closes a bracket to be matched.
    :param macro: Look for this as the macro name before the expression start. If none is given, it 
        is assumed that it starts directly with the expression.
    :return: Length of the expression as int.
    """

    start_position = position
    special_chars = r'\&%$#_{}~^'

    if macro:
        if search_string[position:position + len(macro)] == macro:
            position += len(macro)
        else:
            raise ValueError("The indicated macro, %s, did not occur at position %i."
                             "Context: %s"
                             % (macro, position, search_string[position:position + 20]))

    if search_string[position] == opener:
        stack = [opener]
        position += 1
    else:
        raise ValueError("The first symbol of the match string must be an opening bracket ({). \n"
                         "Context: %s" % search_string[position:position + 50])

    while len(stack) > 0:
        try:
            symbol = search_string[position]
            if symbol == opener:
                stack.append(symbol)
            elif symbol == closer:
                stack.pop()
            elif symbol == '\\' and search_string[position + 1] in special_chars:
                position += 1
            position += 1
        except IndexError:
            raise ValueError("Unbalanced brackets. "
                             "The provided string terminated before all brackets were closed.")
    return position - start_position


def list_maintext_words(search_string=''):
    """
    Create a list of all the words that will end up in the main text.

    :param search_string: The string to create list of.
    :return: List of words
    """

    def add_word_to_list(w, wlist):
        """
        If `word` is not empty, add it to the `word_list` and return the list.

        :param w: Word value to be checked.
        :param wlist: The list it should be added to.
        :return: The (possibly opdated) wordlist.
        """
        if w is not '':
            wlist.append(w)
        return ''

    word_list = []

    ignored_macros = [
        'Afootnote',
        'Bfootnote',
        'Cfootnote',
        'Dfootnote',
        'Efootnote',
        'lemma',
        'index'
    ]

    position = 0
    word = ''
    unicode_words = re.compile('\w')
    while position < len(search_string):
        symbol = search_string[position]
        if re.match(unicode_words, symbol):
            word += symbol
            position += 1
        elif symbol == '\\':
            position += 1
            macro = re.match(r'[^ {[]+', search_string[position:]).group(0)
            if macro not in ignored_macros:
                position += len(macro) + 1
            else:
                position += len(macro)
                if search_string[position] == '[':
                    position += macro_expression_length(search_string[position:],
                                                        opener='[', closer=']')
                if search_string[position] == '{':
                    position += macro_expression_length(search_string[position:])

            word = add_word_to_list(word, word_list)

        elif re.match('\W', symbol):
            word = add_word_to_list(word, word_list)
            position += 1
    # Add the final word to the list.
    add_word_to_list(word, word_list)

    return word_list


def search_in_proximity(search_word, context_before, context_after):
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
    def flatten_list(input_list):
        """Return a flat list from an arbitrarily nested list."""
        for item in input_list:
            if type(item) == list:
                yield from flatten_list(item)
            else:
                yield item

    contexts = flatten_list(context_before + context_after)

    for context_chunk in contexts:
        maintext_words = ' '.join(list_maintext_words(context_chunk))
        if re.search(r'\b' + search_word + r'\b', maintext_words):
            return True
    return False


def replace_in_proximity(context_before_list, context_after_list, search_word):
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

    def replace_in_context_list(context_list, word):
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


def replace_in_string(replace_word, replace_string, lemma_level=0):
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
    def move_punctuation(input_list):
        """Given a list of words, if the item ends in a punctuation character, move the character 
        into new subsequent item """
        return_list = []
        for item in input_list:
            try:
                if item[-1] in ',.?!;':
                    return_list.append(item[:-1])
                    return_list.append(item[-1])
                else:
                    return_list.append(item)
            except IndexError:
                return_list.append(item)
        return return_list

    def check_list_match(pattern_list, replace_list, return_list=list()):
        """Check whether a word string in `pattern_list` (search phrase) is matched in 
        `replace_list`. 
        
        Check whether first item of `pattern_list` is contained in first item of 
        `replace_list`. If it does, move on to next item in `pattern_list` until it is exhausted. 
        This way it matches whole string of words specified in `pattern_list` in `replace_list`.
        
        When the caller of this function iterates through the `replace_list`, it is incrementally 
        checked in full. We want to keep the formatting of the search list, so items from that 
        are returned in order as they are. 
        
        :param pattern_list: List of search words to be matched in `replace_list`.
        :param replace_list: List of words to be matched.
        :param return_list: The results to be returned, built successively in recursive calls. 
        :return List of items from `replace_list` that match items in `pattern_list`.
        """
        try:
            if re.search(r'\b' + pattern_list[0] + r'\b', replace_list[0]):
                return_list.append(replace_list[0])
                return check_list_match(pattern_list[1:], replace_list[1:], return_list)
        except IndexError:
            return return_list

    def make_replacements(search_list, replacement_list, updated_list=list()):
        """
        Iterate the content of the `replacement_list` and wrap it in `\sameword{}` if necessary.
          
        This function iterates over each word in the `replacement_list` and checks whether it ( 
        along with subsequent words, when applicable) match the content of the `search_list` with 
        the `check_list_match` function. When that is the case, the item(s) are wrapped in 
        `\sameword{}`. 
        
        When returning the updated list, a bit of whitespace cleanup is performed on it.
         
        :param search_list: List of words that should be matched in sequence. 
        :param replacement_list: The string of words that should be checked for matches.
        :param updated_list: The updated list. Empty by default. Argument in recursive calls. 
        :return: The updated list in full.
        """
        match_in_replace_list = check_list_match(search_list, replacement_list, return_list=[])
        try:
            if match_in_replace_list:
                updated_list.append(
                    wrap_phrase(' '.join(match_in_replace_list), lemma_level=lemma_level))
                return make_replacements(
                    search_list, replacement_list[len(match_in_replace_list):], updated_list)
            updated_list.append(replacement_list[0])
            return make_replacements(search_list, replacement_list[1:], updated_list)
        except IndexError:
            return re.sub(' ([.,;:?])', r'\1', ' '.join(updated_list))

    unwrapped = False
    try:
        if replace_string[0] is '{' and replace_string[-1] is '}':
            replace_string = replace_string[1:-1]
            unwrapped = True
    except IndexError:
        # The input replacement string is empty, so just return with processing.
        return replace_string

    replacement_string_listed = move_punctuation(replace_string.split(' '))
    search_word_listed = replace_word.split(' ')
    updated_replacement = make_replacements(search_word_listed, replacement_string_listed)

    if unwrapped:
        return '{' + updated_replacement + '}'
    return updated_replacement


def wrap_phrase(phrase, lemma_level=0):
    """
    Wrap the word or phrase in the appropriate \sameword{}-element.
    
    This means that if the word or phrase is already wrapped in a \sameword{}, it cannot be 
    wrapped in another. If one or more words of a phrase are wrapped, it should wrap the whole 
    phrase. It also needs to handle the conditions of lemma level numbering. 
    
    :param phrase: the word or phrase that should be wrapped. 
    :param lemma_level: the level of the lemma annotation. Default=0
    :return: The wrapped input phrase
    """
    macro_match = re.match(r'\\([^{\[]+)([^{]+)?{', phrase)  # match initial macro
    prefix_macro = ''
    if macro_match and 'sameword' not in macro_match.group(1):
        prefix_macro = macro_match.group(0)
        phrase = phrase[len(prefix_macro):]

    # Should we handle the lemma level?
    if lemma_level is not 0:
        this_level = '[' + str(lemma_level) + ']'
    else:
        this_level = ''

    # Is the phrase wrapped?
    sameword_pattern = re.compile(r'(\\sameword)([^{]+)?{')
    pattern_match = re.match(sameword_pattern, phrase)
    exact_wrap = False
    extended_wrap = False
    existing_level = None
    sameword_match = None
    if pattern_match:
        sameword_match = pattern_match.group(0)
        existing_level = pattern_match.group(2)
        sameword_match_length = macro_expression_length(phrase, macro=sameword_match[:-1])
        if sameword_match_length == len(phrase):
            # The whole phrase is wrapped.
            exact_wrap = True
        elif re.match('}+', phrase[sameword_match_length:]):
            # After the closing of the wrapped phrase, there are more closing (unbalanced) brackets.
            extended_wrap = True

    if exact_wrap:
        if existing_level:
            # Wrap contains level indication
            if this_level is '':
                # If lemma level of current annotation is None, keep the existing level argument.
                this_level = existing_level
            else:
                # If we have a lemma level here, combine with existing level argument.
                this_level = this_level[:-1] + ',' + existing_level[1:]

        if this_level:
            updated_phrase = phrase.replace(sameword_match, r'\sameword' + this_level + '{')
        else:
            updated_phrase = phrase
    else:
        if extended_wrap:
            updated_phrase = phrase.replace(sameword_match, r'\sameword' + this_level + '{')
        else:
            updated_phrase = r'\sameword' + this_level + '{' + phrase + '}'
    return prefix_macro + updated_phrase

def critical_note_match_replace_samewords(text):
    """
    The main search and replace function.

    The included function `sub_processing` is the one doing all the work, and this wrapper only 
    splits the input string into a list and joins the result of the sub-process for returning. We 
    can't do that as one function as the recursive processing works best with lists as input and 
    return values. 

    The basic idea is to split the string into a list of items that are either `\edtext{
    }`-elements or not (using the `edtext_split` function). Then for each item that is an 
    `\edtext{}`-element, check whether there are duplicates of some of its content that would 
    result in an ambiguous apparatus note. When potentially ambiguous apparatus entries are 
    identified, wrap the words in the context and the apparatus note in a `\sameword{}`. 

    This algorithm is based on the assumption that `\lemma{}` is always used on the apparatus 
    notes. 

    The function is recursive, so if an `\edtext{}`-element contains another `\edtext{}`-element, 
    run the function on that first. The algorithm starts from the inside out, thus processing the 
    most deeply nested apparatus note(s) first. 

    Search and replace in proximity works like this: Receive a list of lists. Each list in the 
    list represents a lemma level. This means that it should iterate proximate words from the 
    last item (which will be the innermost context) until it reaches end of list or max word 
    count. Replacement: The replacement uses the proximity word building, so it would take the 
    same approach, replacing the amount necessary. Replacement would then be a matter of updating 
    the context_before and context_after lists. 

    TODO: Remove requirement of `\lemma{}` element.

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
