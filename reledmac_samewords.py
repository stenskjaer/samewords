import re

__version__ = '0.0.1'

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
            raise ValueError("Unbalanced brackets. The provided string terminated before all brackets were closed.")
    return position - start_position


def list_maintext_words(search_string=''):
    """
    Create a list of all the words that will end up in the main text.

    :param search_string: The string to create list of.
    :return: List of words
    """
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


def iter_proximate_words(input_list, index=0, word_count_sum=0, side='', length=30):
    """
    Get a suitable amount of items from input_list to serve 30 proximity words for analysis.

    When the `side` is `left`, it will return the list reversed thereby yielding the items closest to the search start.

    :param input_list: The list to pull from
    :param index: The index from where the search should start.
    :param word_count_sum: Accumulative word counter for finding the right size chunk.
    :param side: Indicate whether we are searching left of the pivot. In that case, we reverse the list too.
    :param length: Amount of words required for the chunk.
    :return: List of at least 30 word on each side of the pivot word (less if we are at the end of the string).
    """

    word_count_sum += len(list_maintext_words(input_list[index]))

    if side == 'left':
        if word_count_sum < length and index > 0:
            return iter_proximate_words(input_list, index - 1, word_count_sum, side)
        else:
            return input_list[index:]
    elif side == 'right':
        if word_count_sum < length and index + 1 < len(input_list):
            return iter_proximate_words(input_list, index + 1, word_count_sum, side)
        else:
            return input_list[:index + 1]
    else:
        raise ValueError("The value of the argumen 'side' must be either 'left' or 'right'. You gave: %s" % side)


def flatten_list(input_list):
    """Return a flat list from an arbitrarily nested list."""
    for item in input_list:
        if type(item) == list:
            yield from flatten_list(item)
        else:
            yield item


def search_in_proximity(search_word, context_before, context_after):
    """
    Check whether a search word is present in the one of two lists. The two input lists contain the context of the
    search word.

    We need to search for a regex demarcating the string with boundaries to make sure we don't just match a partial
    word ("so" matching "something"). We can't demarcate by whitespace, as that may not always be present.

    :param search_word: The word we look for.
    :param context_before: List of preceding context to be searched.
    :param context_after: List of following context to be searched.
    :return: Boolean.
    """
    contexts = flatten_list(context_before + context_after)

    for context_chunk in contexts:
        # We need to search the maintext cleaned string. But this seems to give a lot of subsequent problems...
        maintext_words = ' '.join(list_maintext_words(context_chunk))
        if re.search(r'\b' + search_word + r'\b', maintext_words):
            return True
    return False


def edtext_split(search_string):
    """
    Split the input `search_string` into list demarcated by `\edtext{}`-items.

    :param search_string: The input string.
    :return: List.
    """

    if r'\edtext' in search_string:
        appnote_start = search_string.find(r'\edtext')
        edtext_length = macro_expression_length(search_string, position=appnote_start, macro=r'\edtext')
        appnote_length = macro_expression_length(search_string, appnote_start + edtext_length)
        appnote_end = appnote_start + edtext_length + appnote_length

        return [search_string[:appnote_start]] + [search_string[appnote_start:appnote_end]] \
               + edtext_split(search_string[appnote_end:])
    else:
        return [search_string]


def replace_in_proximity(context_before_list, context_after_list, search_word):
    """
    Replace a specified search word in two lists containing the text surrounding a chunk of text.

    This is used for replacing a word that is present in an `\edtext{}`-element and that is confirmed to be in the
    proximate context.

    The replacement is only done on the proximity of the pivot element.

    :param search_word: The word to be replaced in surrounding text.
    :param context_after_list: The context list contaning the preceding content.
    :param context_before_list: The context list contaning the following content.
    :return: The two updated lists where samewords of the search word are marked.
    """

    def replace_in_context_list(context_list, word, side=''):
        for item_index, context_item in enumerate(context_list):
            if side == 'right':
                chunk_list = iter_proximate_words(context_item, side=side)
            elif side == 'left':
                # When left, we get proximate words from the end, as it is closest to the pivot element.
                chunk_list = iter_proximate_words(context_item, side=side, index=len(context_item) - 1)

            for index, chunk in enumerate(chunk_list):
                chunk = replace_in_string(word, chunk)
                chunk_list[index] = chunk
            context_list[item_index] = chunk_list
        return context_list

    left = replace_in_context_list(context_before_list, search_word, side='left')
    right = replace_in_context_list(context_after_list, search_word, side='right')

    return left, right


def replace_in_string(search_word, search_string):
    """
    Recursively replace the search word in the search string with a version that is wrapped in sameword. This only
    replaces on words that do are not already wrapped in a sameword.

    :return: Updated or unchanged string.
    """
    positions = [item.start() for item in re.finditer(r'\b' + search_word + r'\b', search_string)
                 if not sameword_wrapped(search_string, item.start())]

    if positions:
        updated_string = search_string[:positions[0]]

        for index, position in enumerate(positions):
            updated_string += r'\sameword{' + search_word + '}'
            try:
                updated_string += search_string[position + len(search_word):positions[index + 1]]
            except IndexError:
                updated_string += search_string[position + len(search_word):]

        return updated_string
    else:
        return search_string


def critical_note_match_replace_samewords(input_string):
    """
    The main search and replace function.

    The included function `sub_processing` is the one doing all the work, and this wrapper only splits the input
    string into a list and joins the result of the sub-process for returning. We can't do that as one function as the
    recursive processing works best with lists as input and return values.

    The basic idea is to split the string into a list of items that are either `\edtext{}`-elements or not (using the
    `edtext_split` function). Then for each item that is an `\edtext{}`-element, check whether there are duplicates
    of some of its content that would result in an ambiguous apparatus note. When potentially ambiguous apparatus
    entries are identified, wrap the words in the context and the apparatus note in a `\sameword{}`.

    This algorithm is based on the assumption that `\lemma{}` is always used on the apparatus notes.

    The function is recursive, so if an `\edtext{}`-element contains another `\edtext{}`-element, run the function on
    that first. The algorithm starts from the inside out, thus processing the most deeply nested apparatus note(s)
    first.

    Search and replace in proximity works like this: Receive a list of lists. Each list in the list represents a
    lemma level. This means that it should iterate proximate words from the last item (which will be the innermost
    context) until it reaches end of list or max word count. Replacement: The replacement uses the proximity word
    building, so it would take the same approach, replacing the amount necessary. Replacement would then be a matter
    of updating the context_before and context_after lists.

    TODO: Remove requirement of `\lemma{}` element.

    :param input_string: The string that should be processed.
    :return: The processed string with encoding of disambiguation.
    """

    def sub_processing(input_list, context_before=list(), context_after=list(), lemma_level=1):

        for pivot_index, edtext_element in enumerate(input_list):

            if r'\edtext' in edtext_element:

                # Build the surrounding context. If is a list of lists. List 0 contains context on lvl 1,
                # list 1 contains context on lvl 2 etc.
                if lemma_level == 1:
                    context_before = [iter_proximate_words(input_list[:pivot_index], side='left')]
                    context_after = [iter_proximate_words(input_list[pivot_index + 1:], side='right')]
                else:
                    inner_context_before = input_list[:pivot_index]
                    inner_context_after = input_list[pivot_index + 1:]

                    # We use lemma level as the number in the list reflects the nest depth.
                    try:
                        context_before[lemma_level - 1] = inner_context_before
                    except IndexError:
                        context_before = context_before + [inner_context_before]
                    try:
                        context_after[lemma_level - 1] = inner_context_after
                    except IndexError:
                        context_after = context_after + [inner_context_after]

                edtext_length = macro_expression_length(edtext_element, position=0, macro=r'\edtext')
                appnote_content = macro_expression_content(edtext_element, edtext_length, capture_wrap=False)
                edtext_content = macro_expression_content(edtext_element, position=len(r'\edtext'), capture_wrap=False)

                if r'\edtext' in edtext_content:
                    # We have a nested apparatus note here, so before moving on, we process that.
                    lemma_level += 1
                    edtext_content, context_before, context_after = sub_processing(
                        edtext_split(edtext_content), context_before=context_before,
                        context_after=context_after, lemma_level=lemma_level
                    )
                    edtext_content = ''.join(edtext_content)
                    edtext_element = r'\edtext{' + edtext_content + '}{' + appnote_content + '}'
                    lemma_level -= 1

                # Check that we have a lemma element.
                if r'\lemma' in appnote_content:
                    lemma_content = macro_expression_content(appnote_content, position=len(r'\lemma'))
                else:
                    raise ValueError('No lemma element found in the apparatus note %s' % appnote_content)

                # Determine lemma type. The `dots` variable is used for processing of ldots notes.
                lemma_word_list = list_maintext_words(lemma_content)
                dots = []
                if re.search(r'\\l?dots({})?', lemma_content):
                    # Covers ldots lemma. We use the dots variable to identify first and last word in dots lemmas.
                    search_words = [lemma_word_list[0]] + [lemma_word_list[-1]]
                    dots = search_words
                elif len(lemma_word_list) == 1:
                    # Covers single word lemma
                    search_words = [lemma_content]
                elif len(lemma_word_list) > 1:
                    # Covers multiword lemma. We join them to one "search_word" as we look for that specific phrase
                    # in proximity, not just any of its containing words.
                    search_words = [' '.join(lemma_word_list)]
                else:
                    search_words = []

                for search_word in search_words:

                    if search_in_proximity(search_word, context_before, context_after):

                        if len(search_word.split(' ')) > 1:
                            # Notice: We must check if a multiword phrase occurs in the proximity. But we only need to
                            # mark up the first word in the phrase with \sameword. In that case, revise search_word to
                            # only first word
                            search_word = search_word.split(' ')[0]

                        # Update the proximate content.
                        context_before, context_after = replace_in_proximity(context_before, context_after, search_word)

                        edtext_element = replace_in_critical_note(
                            edtext_element, search_word, lemma_level=lemma_level, dots=dots)
                        edtext_element = replace_in_critical_note(
                            edtext_element, search_word, lemma_level=lemma_level, in_lemma=True)

                # We build the return list as a separate variable as we need to pull material from the input list. As
                #  the proximate replacements may not cover whole text, we wrap it all with all preceding and
                # following content, if any.
                proximate_before = context_before.pop()
                proximate_after = context_after.pop()
                output_list = input_list[:pivot_index - len(proximate_before)]
                output_list += proximate_before
                output_list += [edtext_element]
                output_list += proximate_after
                output_list += input_list[len(proximate_after) + pivot_index + 1:]
                input_list = output_list

        return input_list, context_before, context_after

    # Remember, `sub_processing` returns three values, we only need the first here.
    result = sub_processing(edtext_split(input_string), context_before=list(), context_after=list(), lemma_level=1)[0]

    return ''.join(result)


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
    if lemma_level is not 0:
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
                return context_string.replace(wrap_search.group(0), r'\sameword' + level_argument + '{' + word + '}')
            else:
                return context_string.replace(word, r'\sameword' + level_argument + '{' + word + '}')
        else:
            if wrap_search:
                # If the word is already wrapped, pass? How about other instances?
                pass
            else:
                return context_string.replace(word, r'\sameword{' + word + '}')


def replace_in_critical_note(search_string, replace_word, lemma_level=1, in_lemma=False, dots=list()):
    """
    Replace all instances of `replace_word` in a apparatus note (full `\edtext{}{}`) and return the updated string.

    This is done by building a string and making replacements as we go along. The function recurses on nested edtext
    elements.

    :param search_string: The string containing the critical note.
    :param replace_word: The word to be replaced.
    :param lemma_level: The level from which the lemma refers to the word to be `replace_word`.
    :param in_lemma: If true, it will replace the search word in lemma element, otherwise it will replace in edtext.
    :param dots: The search words in case we are in a lemma containing a version of `\dots`.
    :return: The updated string.
    """

    position = len(r'\edtext')

    return_string = search_string[:position]

    edtext_content_string = macro_expression_content(search_string, position, capture_wrap=True)
    edtext_content_list = edtext_split(edtext_content_string)

    # Should we replace in edtext or lemma?
    if in_lemma is False:

        # We are in the edtext
        # Is there a nested critical note?

        if dots:
            # We have a ldots lemma, so we only replace a the beginning and end of the edtext element.
            if replace_word == dots[0]:
                edtext_content_list[0] = wrap_in_sameword(replace_word, edtext_content_list[0], lemma_level)
            elif replace_word == dots[1]:
                edtext_content_list[len(edtext_content_list) - 2] \
                    = wrap_in_sameword(replace_word, edtext_content_list[len(edtext_content_list) - 2], lemma_level)
            return_string += ''.join(edtext_content_list)
        else:

            for pivot_index, edtext_content in enumerate(edtext_content_list):

                if r'\edtext' in edtext_content:

                    # Replace up to sub critical note (using a temporary return_string
                    edtext_position = edtext_content.find(r'\edtext{')
                    sub_return_string = wrap_in_sameword(replace_word, edtext_content[:edtext_position], lemma_level)

                    # Replace inside edtext, calling this function. First we need the location of the sub critical note.
                    sub_edtext_length = macro_expression_length(edtext_content,
                                                                position=edtext_position, macro=r'\edtext')
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

        lemma_content = macro_expression_content(search_string[position:], position=len(r'{\lemma'))

        return_string += r'{\lemma{'
        position += len(r'{\lemma{')
        return_string += wrap_in_sameword(replace_word, lemma_content, lemma_level=0)

        position += len(lemma_content)

    # Add the following app note, where nothing should be changed, and return it
    return_string += search_string[position:]

    return return_string
