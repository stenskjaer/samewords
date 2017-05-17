import re


def macro_expression_content(search_string, position=0, opener='{', closer='}', capture_wrap=False):
    """Get the content of a latex expression that has been opened with "{" to any
    level of macro nesting until closing "}".

    This function expects the character at the starting position of the match string to be an
    opening bracket and will complain if it is not. This means that it
    initializes the stack with that opening bracket in the stack. When the
    stack is empty, we have reached the end of the expression, and should
    return the string capture thus far.

    :param search_string: The string to be processed.
    :param position: The starting position in the string [default: 0].
    :param opener: Symbol that opens bracket set [default='{'].
    :param closer: Symbol that closes bracket set [default='}'].
    :param capture_wrap: Capture the wrapping (outermost) brackets [default=False].
    :return: The string captured.
    """

    special_chars = r'\&%$#_{}~^'
    capture = ''

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
    opening bracket and will complain if it is not. Actually it just finds the position where those two are balanced and 
    returns that. 

    :param search_string: The string to be processed.
    :param position: The starting position in the string [default: 0].
    :param opener: The character that opens a bracket to be matched.
    :param closer: The character that closes a bracket to be matched.
    :param macro: Look for this as the macro name before the expression start. If none is given, it is assumed that it 
        starts directly with the expression.
    :return: Length of the expression as int. 
    """

    start_position = position
    special_chars = r'\&%$#_{}~^'

    if macro:
        if search_string[position:position + len(macro)] == macro:
            position += len(macro)
        else:
            raise ValueError("The indicated macro, %s, did not occur at position %i."
                             "Context: %s" % (macro, position, search_string[position:position + 20]))

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
            raise ValueError("Unbalanced brackets. The provided string terminated before all "
                             "brackets were closed.")
    return position - start_position


def list_maintext_words(search_string=''):
    """
    Create a list of all the words that will end in the main text.

    :param search_string: The string to create list of.
    :return: List of words
    """
    import re

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
                    position += macro_expression_length(search_string[position:], opener='[', closer=']')
                if search_string[position] == '{':
                    position += macro_expression_length(search_string[position:])

            word = add_word_to_list(word, word_list)

        elif re.match('\W', symbol):
            word = add_word_to_list(word, word_list)
            position += 1
    else:
        word = add_word_to_list(word, word_list)

    return word_list

def add_word_to_list(word, word_list):
    """
    If `word` is not empty, add it to the `word_list` and return the list.
    
    :param word: Word value to be checked. 
    :param word_list: The list it should be added to.
    :return: The (possibly opdated) wordlist.
    """
    if word is not '':
        word_list.append(word)
    return ''


def iter_proximate_words(input_list, pivot, index=0, word_count_sum=0, side='', length=30):
    """
    Get a suitable amount of items from input_list to serve 30 proximity words for analysis.

    :param input_list: The list to pull from 
    :param pivot: Index of item that the accumulation revolves around (starting point).
    :param index: The index from where the search should start.
    :param word_count_sum: Accumulative word counter for finding the right size chunk.
    :param side: Indicate whether we are searching left of the pivot. In that case, we reverse the list too.
    :param length: Amount of words required for the chunk.
    :return: List of at least 30 word on each side of the pivot word (less if we are at the end of the string).
    """

    word_count_sum += len(list_maintext_words(input_list[index]))

    if side == 'left':
        if word_count_sum < length and index > 0:
            return iter_proximate_words(input_list, pivot, index - 1, word_count_sum, side)
        else:
            return input_list[index:pivot]
    elif side == 'right':
        if word_count_sum < length and index + 1 < len(input_list):
            return iter_proximate_words(input_list, pivot, index + 1, word_count_sum, side)
        else:
            return input_list[pivot + 1:index + 1]
    else:
        raise ValueError("The value of the argumen 'side' must be either 'left' or 'right'. You gave: %s" % side)


def search_in_proximity(search_word, context_list, pivot_index):
    """
    Check whether a search word demarcated by word boundary is present in the proximate part of a string. We need the 
    regex to make sure we don't just match a partial word ("so" matching "something"). We can't demarcate by 
    whitespace, as that may not always be present. 

    :param search_word: The word we look for. 
    :param context_list: The context list in which we search.
    :param pivot_index: The item number in the context list in which the searchword is present.
    :return: 
    """

    # We need to search the maintext cleaned string. But this seems to give a lot of subsequent problems...
    left_string = ' '.join(list_maintext_words(''.join(
        iter_proximate_words(context_list, pivot=pivot_index, index=pivot_index-1, side='left'))))
    right_string = ' '.join(list_maintext_words(''.join(
        iter_proximate_words(context_list, pivot=pivot_index, index=pivot_index+1, side='right'))))

    if re.search(r'\b' + search_word + r'\b', left_string) or re.search(r'\b' + search_word + r'\b', right_string):
        return True
    return False


def edtext_split(search_string):
    """Return list of strings demarcated by edtext macros."""

    if r'\edtext' in search_string:
        appnote_start = search_string.find(r'\edtext')
        edtext_length = macro_expression_length(search_string, position=appnote_start, macro=r'\edtext')
        appnote_length = macro_expression_length(search_string, appnote_start + edtext_length)
        appnote_end = appnote_start + edtext_length + appnote_length

        return [search_string[:appnote_start]] + [search_string[appnote_start:appnote_end]] \
               + edtext_split(search_string[appnote_end:])
    else:
        return [search_string]


def replace_in_proximity(split_list, pivot_index, search_word):
    #  make recursive function building a nested list with enough words, but not too many.
    left = iter_proximate_words(split_list, pivot=pivot_index, index=pivot_index - 1, side='left')
    right = iter_proximate_words(split_list, pivot=pivot_index, index=pivot_index + 1, side='right')

    for left_item, left_chunk in enumerate(left):
        search_word_position = left_chunk.find(search_word)
        if not sameword_wrapped(left_chunk, search_word_position):
            split_list[pivot_index - (left_item + 1)] = left_chunk.replace(search_word,
                                                                           r'\sameword{' + search_word + '}')
    for right_item, right_chunk in enumerate(right):
        search_word_position = right_chunk.find(search_word)
        if not sameword_wrapped(right_chunk, search_word_position):
            split_list[pivot_index + (right_item + 1)] = right_chunk.replace(search_word,
                                                                             r'\sameword{' + search_word + '}')
    return split_list


def critical_note_match_replace_samewords(input_list, context_list=list(), lemma_level=1, context_list_index=0):
    if not context_list:
        context_list = input_list

    for pivot_index, edtext_element in enumerate(input_list):

        # We need to same the level one list index for context replacement.
        if lemma_level == 1:
            context_list_index = pivot_index

        if r'\edtext' in edtext_element:

            edtext_length = macro_expression_length(edtext_element, position=0, macro=r'\edtext')
            appnote_content = macro_expression_content(edtext_element, edtext_length, capture_wrap=False)
            edtext_content = macro_expression_content(edtext_element, position=len(r'\edtext'), capture_wrap=False)

            if r'\edtext' in edtext_content:
                lemma_level += 1

                edtext_content = critical_note_match_replace_samewords(edtext_split(edtext_content),
                                                                       context_list=context_list,
                                                                       lemma_level=lemma_level,
                                                                       context_list_index=context_list_index)
                edtext_element = r'\edtext{' + ''.join(edtext_content) + '}{' + appnote_content + '}'
                lemma_level -= 1

            if r'\lemma' in appnote_content:
                lemma_content = macro_expression_content(appnote_content, position=len(r'\lemma'))
            else:
                raise ValueError('No lemma element found in the apparatus note %s' % appnote_content)

            # Determine lemma type.
            lemma_word_list = list_maintext_words(lemma_content)
            if (r'\ldots' or r'\dots') in lemma_content:
                # Covers ldots lemma.
                search_words = [lemma_word_list[0]] + [lemma_word_list[-1]]
            elif len(lemma_word_list) == 1:
                # Covers single word lemma
                search_words = [lemma_content]
            elif len(lemma_word_list) > 1:
                # Covers multiword lemma
                search_words = [' '.join(lemma_word_list)]
            else:
                search_words = []

            for search_word in search_words:

                if search_in_proximity(search_word, context_list, context_list_index):
                    # Match of current word, so we need to mark it in proximity and current critical note.

                    if len(search_word.split(' ')) > 1:
                        # Notice: We must check if a multiword phrase occurs in the proximity. But we only need to
                        # mark up the first word in the phrase with \sameword. In that case, revise search_word to
                        # only first word
                        search_word = search_word.split(' ')[0]

                    replace_in_proximity(context_list, context_list_index, search_word)

                    edtext_element = replace_in_critical_note(
                        edtext_element, search_word, lemma_level=lemma_level)
                    edtext_element = replace_in_critical_note(
                        edtext_element, search_word, lemma_level=lemma_level, in_lemma=True)

            input_list[pivot_index] = edtext_element

    return ''.join(input_list)


def sameword_wrapped(context_string, word_position):
    """
    Check if the provided string is already wrapped in a sameword macro

    :param context_string: The immediate context of the word 
    :param word_position: The position of the word being checked in the context string.
    :return: Boolean
    """
    if context_string[word_position - len(r'\sameword{'):word_position] == r'\sameword{':
        return True
    return False


def wrap_in_sameword(word, context_string, lemma_level=0):

    position = context_string.find(word)
    if lemma_level > 0:
        lemma_level = str(lemma_level)
        level_argument = '[' + lemma_level + ']'
    else:
        level_argument = None

    if position is not None:
        wrap_search = re.search(r'(\\sameword)([^{]+)?{' + word + '}', context_string)
        if wrap_search:
            # Word already wrapped.
            if wrap_search.group(2):
                # Wrap contains level indication
                existing_level = wrap_search.group(2)
                level_argument = '[' + lemma_level + ',' + existing_level[1:]

        if level_argument:
            if wrap_search:
                return context_string.replace(wrap_search.group(0),
                                              r'\sameword' + level_argument + '{' + word + '}')
            else:
                return context_string.replace(word, r'\sameword' + level_argument + '{' + word + '}')
        else:
            if wrap_search:
                # If the word is already wrapped, pass? How about other instances?
                pass
            else:
                return context_string.replace(word, r'\sameword{' + word + '}')


def replace_in_critical_note(search_string, replace_word, return_string='', lemma_level=1, in_lemma=False):
    """
    Given a critical note starting from the \edtext macro, replace all instances of specified word at any level of 
    critical note, without touching the content of the apparatus note. 

    :param search_string: The string containing the critical note. 
    :param replace_word: The word to be replaced.
    :param return_string: The string that will be returned. This should be left blank on first level call.
    :param lemma_level: The level from which the lemma refers to the word to be `replace_word`.
    :param in_lemma: If true, it will replace the search word in lemma element, otherwise it will replace in edtext.
    :return: The updated string.
    """

    position = len(r'\edtext')

    return_string += search_string[:position]

    edtext_content_string = macro_expression_content(search_string, position, capture_wrap=True)
    edtext_content_list = edtext_split(edtext_content_string)

    # Should we replace in edtext or lemma?
    if in_lemma is False:

        # We are in the edtext
        # Is there a nested critical note?
        for pivot_index, edtext_content in enumerate(edtext_content_list):

            if r'\edtext' in edtext_content:

                # Replace up to sub critical note (using a temporary return_string
                edtext_position = edtext_content.find(r'\edtext{')
                sub_return_string = wrap_in_sameword(replace_word, edtext_content[:edtext_position], lemma_level)

                # Replace inside edtext, calling this function. First we need the location of the sub critical note.
                sub_edtext_length = macro_expression_length(edtext_content, position=edtext_position, macro=r'\edtext')
                sub_appnote_length = macro_expression_length(edtext_content,
                                                             position=edtext_position + sub_edtext_length)
                sub_critnote_end = edtext_position + sub_edtext_length + sub_appnote_length
                sub_return_string += replace_in_critical_note(edtext_content[edtext_position:sub_critnote_end],
                                                              replace_word, lemma_level=lemma_level)

                # Relace rest of current edtext from after sub critical note
                sub_return_string += wrap_in_sameword(replace_word, edtext_content[sub_critnote_end:], lemma_level)
                edtext_content_list[pivot_index] = sub_return_string

            else:
                edtext_content_list[pivot_index] = wrap_in_sameword(replace_word, edtext_content, lemma_level)

            return_string += edtext_content_list[pivot_index]

        # Bump position to end of edtext_content
        position += len(edtext_content_string)

    else:
        # In lemma: Add edtext content and bump position to after that.
        return_string += edtext_content_string
        position += len(edtext_content_string)

        lemma_length = macro_expression_length(search_string[position:], macro=r'{\lemma')

        return_string += wrap_in_sameword(replace_word, search_string[position:position + lemma_length], lemma_level=0)

        position += lemma_length

    # Add the following app note, where nothing should be changed, and return it
    return_string += search_string[position:]

    return return_string
