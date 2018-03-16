import re

from collections import UserString, UserList
from typing import List, Tuple, Dict, Union
from operator import itemgetter

from samewords.brackets import Brackets
from samewords.settings import settings

RegistryEntry = Dict[str, Union[List[int], int]]
Registry = List[RegistryEntry]


class Element:
    def __init__(self, cont: str, pos: int) -> None:
        self.cont = cont
        self.pos = pos

    def __repr__(self) -> str:
        return "({}, {})".format(self.cont, self.pos)


class Macro(UserString):
    """A latex macro, holding information in its name and optional arguments.
    TODO: Don't gobble up the whole following string in matching.
    """

    def __init__(self, input_string: str = '',
                 pos: int = None, end: int = None) -> None:
        self.data = input_string
        super().__init__(self)
        self.name = self._identify_name()
        self.oarg = self._optional_argument()
        self.opening = re.match(re.escape(self.name + self.oarg + '{'),
                                self.data)
        self.empty = self._is_empty()
        self.pos = pos              # register start index in word
        self.end = end
        self.to_closing = False     # Distance in wordlist to closing bracket.
        self.hidden_content = ''    # Content that won't count as words

    def __len__(self) -> int:
        return len(self.full())

    def __repr__(self) -> str:
        return "'{}'".format(self.full())

    def __str__(self) -> str:
        return str(self.full())

    def __eq__(self, other) -> bool:
        return self.full() == other

    def _identify_name(self) -> str:
        """
        A TeX macro can be '\' followed by either a string of letters or
        any single character. Find that.
        """
        if self.data is not '':
            return re.match(r'\\(\w+|.)', self.data).group(0)

    def _optional_argument(self) -> str:
        """
        Identify the possible optinal argument of the marco.
        """
        match = re.match(re.escape(self.name) + r'(\[[^\]]+\])', self.data)
        if match:
            return match.group(1)
        return ''

    def _is_empty(self) -> bool:
        """
        If the macro contains an opening bracket that is not followed
        immediately by a closing bracket, it has some content.
        """
        if self.opening:
            try:
                return self.data[len(self.opening.group(0))] == '}'
            except IndexError:
                # String ends after opening, so we assume it will have content.
                return False
        # It has no opening, so it has no content.
        return True

    def full(self) -> str:
        if self.data is '':
            return ''
        elif self.opening:
            if self.hidden_content:
                return self.opening.group(0) + self.hidden_content[1:]
            else:
                return self.opening.group(0)
        else:
            return self.name


class Word(UserString):
    """
    Attributes:
        self.clean_apps: A list of apparatus elements that will be used for
        search word analysis.
        self.ann_apps: A list of apparatus elements that will get annotated.
    """

    def __init__(self, chars: str = '') -> None:

        self.data = chars
        super().__init__(self)
        self.spaces = ''
        self.comment: List[Element] = []
        self.suffixes: List[Element] = []
        self.content: List[Element] = []
        self.punctuation: List[Element] = []
        self.clean_apps: List[Element] = []     # clean apps for analysis
        self.ann_apps: List[Element] = []       # annotation apps
        self.macros: List[Macro] = []
        self.edtext_start = False
        self.edtext_end = False
        self.has_sameword = False

    def __str__(self) -> str:
        return str(self.get_text())

    def __repr__(self) -> str:
        return "'{}'".format(self.get_text())

    def __eq__(self, other) -> bool:
        return self.get_text() == other

    def __len__(self):
        return len(self.full())

    def lower(self):
        return ''.join([w.cont.lower() for w in self.content])

    def get_text(self) -> str:
        return ''.join([c.cont for c in self.content])

    def add_app_entry(self, input_string: str, pos: int, index: int = None):
        """Add apparatus entry to the registry list and return string. If the
        index is provided, add to that index of the list, otherwise append. """
        if index:
            new_cont = self.clean_apps[index].cont + input_string
            pos = self.clean_apps[index].pos
            self.clean_apps[index] = Element(new_cont, pos)
        else:
            self.clean_apps.append(Element(input_string, pos))

    def full(self) -> str:
        """
        :return: full word including prefix and suffix.
        """
        elements = (
                [[e.cont, e.pos] for e in self.comment] +
                [[e.cont, e.pos] for e in self.content] +
                [[e.full(), e.pos] for e in self.macros] +
                [[e.cont, e.pos] for e in self.punctuation] +
                [[e.cont, e.pos] for e in self.ann_apps] +
                [[e.cont, e.pos] for e in self.clean_apps] +
                [[e.cont, e.pos] for e in self.suffixes]
        )
        elements.sort(key=itemgetter(1))
        return ''.join([element[0] for element in elements]) + self.spaces

    def close_macro(self, distance: int):
        """If there are any open macros on the word, close the last of those.
        This means that we close inner macros first."""
        if self.macros:
            for macro in reversed(self.macros):
                if macro.opening and macro.to_closing is False:
                    macro.to_closing = distance
                    return True
        raise IndexError('The word does not have any open macros.')

    def _increment_after(self, element: Union[Macro, Element],
                             increment: int) -> None:
        elements = [self.comment, self.macros, self.content, self.suffixes,
                    self.clean_apps, self.ann_apps, self.punctuation]
        for el in elements:
            for item in el:
                if item.pos >= element.pos and item is not element:
                    item.pos += increment

    def _decrement_after(self, pos: int, decrement: int) -> None:
        elements = [self.comment, self.macros, self.content, self.suffixes,
                    self.clean_apps, self.ann_apps, self.punctuation]
        for el in elements:
            for item in el:
                if item.pos > pos:
                    item.pos -= decrement

    def update_element(self, elem: Element, cont: str) -> None:
        incr = len(cont) - len(elem.cont)
        elem.cont = cont
        self._increment_after(elem, incr)

    def update_macro(self, macro: Macro, index: int) -> None:
        """Update the macro at index. """
        old = self.macros[index]
        macro.pos = old.pos
        macro.to_closing = old.to_closing
        increment = len(macro) - len(old)
        self._increment_after(macro, increment)
        self.macros[index] = macro

    def add_macro(self, macro: Macro, index: int = None) -> None:
        """Wrap the word in a macro. If desired it can add the macro at the
        given index and move the existing macro. The wrapping needs to update
        the positions in the word. It must wrap the word, which means the
        position of the macro must be less than the position of the content
        start. """
        if index is not None:
            old = self.macros[index]
            macro.pos = old.pos
            increment = len(macro) - len(old)
            self._increment_after(macro, increment)
            self.macros[index] = macro
            self.macros.append(old)
        else:
            positions = sorted([cont.pos for cont in self.content])
            if positions:
                # With content add macro before first content pos.
                pos = positions[0]
            elif self.macros:
                # No content but macros, add the macro after last macro end.
                pos = len(self.macros[-1]) + self.macros[-1].pos
            else:
                # Then I don't know what to do so just add at front.
                pos = 0
            macro.pos = pos
            increment = len(macro)
            self._increment_after(macro, increment)
            self.macros.append(macro)

    def pop_macro(self, index: int = -1) -> Macro:
        """Remove the macro from the word at the given index."""
        m = self.macros.pop(index)
        self._decrement_after(m.pos, len(m))
        return m

    def append_suffix(self, content: str) -> None:
        """This adds the suffix string to the list with a position after the
        last. """
        if self.content:
            # last element in self.content.
            last = sorted(self.content, key=lambda e: e.pos)[-1]
            end_pos = last.pos
            end_len = len(last.cont)
            pos = end_pos + end_len
        elif self.suffixes:
            pos = sorted([i.pos for i in self.suffixes], reverse=True)[0] + 1
        elif self.clean_apps:
            pos = sorted([i.pos for i in self.clean_apps])[0]
        elif self.punctuation:
            pos = sorted([i.pos for i in self.punctuation], reverse=True)[0] + 1
        else:
            raise ValueError(
                'The correct position for the suffix could not be determined'
                'Word: {}'.format(self.full())
            )
        new = Element(content, pos)
        self._increment_after(new, len(content))
        self.suffixes.append(new)

    def pop_suffix(self, index=-1):
        """Remove the suffix from the word at the given index."""
        m = self.suffixes.pop(index)
        self._decrement_after(m.pos, len(m.cont))
        return m


class Words(UserList):
    """A list of Word objects with a couple of custom methods."""

    def __init__(self, initlist: List[Word] = None):
        self.data = []
        super().__init__(self)
        if initlist is not None:
            if type(initlist) == type(self.data):
                self.data[:] = initlist
            elif isinstance(initlist, UserList):
                self.data[:] = initlist.data[:]
            else:
                self.data = list(initlist)

    def __getitem__(self, index):
        cls = type(self)
        if isinstance(index, slice):
            return cls(self.data[index])
        elif isinstance(index, int):
            return self.data[index]
        else:
            msg = '{cls.__name__} indices must be integers'
            raise TypeError(msg.format(cls=cls))

    def index(self, item, default=0):
        for idx, val in enumerate(self.data):
            if val.get_text().lower() == item.lower():
                return idx
        return default

    def rindex(self, item, default=0):
        """Get the index of the first example of item from the right,
        and return the index numbered from the left. """
        for idx, val in enumerate(reversed(self.data)):
            if val.get_text().lower() == item.lower():
                return len(self) - idx - 1
        return default

    def write(self) -> str:
        return ''.join([w.full() for w in self.data])

    def clean(self) -> List:
        """A list strings of each Word.text item, i.e. a cleaned word list."""
        return [w.get_text() for w in self.data if w.content]


class Tokenizer:

    def __init__(self, input_str: str = '') -> None:
        """
        self.edtext_brackets: registry of opened brackets at the beginning of
        each edtext macro. Each integer corresponds to a higher level of
        nested edtexts. When a } is hit and the edtext_brackets of that level
        is reached, the encountered } closes the edtext.

        :param input_str: The input string that will be tokenized.
        """
        self.data = input_str
        # Recognized punctuation characters
        self._punctuation = re.compile(
            r'[{}]+'.format(''.join(settings['punctuation']))
        )
        # Characters that need to be escaped in LaTeX
        self._escape_chars = '\\&%$#_{}~^'
        # keep track of current nesting level (zero indexed, so we start at -1)
        self._edtext_lvl = -1
        # keep track of opened brackets at any point
        self._brackets = 0
        # keep track of closing elements in registry process
        self._closures = 0
        # open brackets when starting edtext, to identify apparatus start
        self._stack_edtext = []
        # for indexing into registry after tokenization
        self._stack_registry = []
        # register open bracket count at different positions
        self._stack_bracket = []
        # index available on whole process
        self._index = 0
        # the words list, which needs to be available during any tokenization.
        self._words: Words = Words()
        # non-content macros that should be ignored.
        self._exclude_macros = settings['exclude_macros']
        # the registry list
        self.registry = []
        self.wordlist = self._wordlist()

    def _wordlist(self) -> Words:
        """
        Run the string by tokenizing from each position (subfunction) and
        register the returned Word object if it either opens or closes an
        edtext element.
        """
        pos = 0
        while pos < len(self.data):
            word, pos = self._tokenize(self.data, pos)
            if word.edtext_start:
                count = len([m for m in word.macros if m.name == r'\edtext'])
                while count > 0:
                    self._stack_registry.append(len(self.registry))
                    self.registry.append({'lvl': 0, 'data': [self._index]})
                    count -= 1
            if word.edtext_end:
                while self._closures > 0:
                    reg_index = self._stack_registry.pop()
                    self.registry[reg_index]['data'].append(self._index)
                    self.registry[reg_index]['lvl'] = self._edtext_lvl
                    self._closures -= 1
                    self._edtext_lvl -= 1
            self._words.append(word)
            self._index += 1
        return self._words

    def _tokenize(self, string: str, pos: int = 0) -> Tuple[Word, int]:
        """
        Idea: Run the string and build a Word object. Collect characters,
        digits and hyphens into word.text property. Punctuation goes four
        attributes, `pre_` and `post_` to word and macro. Macros enclosing
        the Word.text are put in the Word.macro property. Opening and closing
        brackets are counted to ensure the timely closing of app notes.
        """
        word = Word()
        while pos < len(string):
            c = string[pos]
            if re.match('[\w\d]', c):
                match = re.match('[\w\d\-\']+', string[pos:]).group(0)
                word.content.append(Element(match, pos))
                pos += len(match)
                continue
            if c.isspace():
                word.spaces = re.match('\s+', string[pos:]).group(0)
                pos += len(word.spaces)
                break
            if re.search(self._punctuation, c):
                # Exception: .5 is part of word, not punctuation.
                if re.match('\.\d', string[pos:]):
                    word.content.append(Element(c, pos))
                    pos += 1
                    continue
                word.punctuation.append(Element(c, pos))
                pos += 1
                continue
            if c == '\\':
                if word.clean_apps:
                    # If we run into a macro for a word that already has one
                    # or more app elements, we should start a new word.
                    break
                if string[pos+1] in self._escape_chars:
                    word.content.append(Element(string[pos:pos+2], pos))
                    pos += 2
                    continue
                macro = Macro(string[pos:])
                macro.pos = pos
                word.macros.append(macro)
                pos += len(macro)
                if macro.name in self._exclude_macros:
                    # If we hit a macro that is not a registered content
                    # macro, skip it (including its content, if any).
                    if macro.opening:
                        pos -= 1    # subtract the opening {
                        bracket_end = pos + len(Brackets(string, pos))
                        macro.hidden_content = string[pos:bracket_end]
                        pos += len(macro.hidden_content)
                        word.close_macro(0)
                    break
                if macro.name == r'\edtext' and not word.content:
                    self._stack_edtext.append(self._brackets)
                    self._edtext_lvl += 1
                    word.edtext_start = True
                if macro.name == r'\sameword':
                    word.has_sameword = True
                if macro.opening:
                    # register position for later closing registration
                    self._stack_bracket.append(self._index)
                    self._brackets += 1
                continue
            if c == '{':
                # Determine of this is an app entry.
                if (self._stack_edtext and
                        self._stack_edtext[-1] == self._brackets):
                    bracket_end = pos + len(Brackets(string, pos))
                    word.add_app_entry(string[pos:bracket_end], pos)
                    if '\\sameword' in string[pos:bracket_end]:
                        word.has_sameword = True
                    word.edtext_end = True
                    pos = bracket_end
                    try:
                        if string[pos] == '}':
                            # Add possible closing of parent first edtext arg
                            word.add_app_entry(string[pos], pos, -1)
                            self._brackets -= 1
                            pos += 1
                    except IndexError:
                        pass
                    self._stack_edtext.pop()
                    self._closures += 1
                    continue
                else:
                    word.suffixes.append(Element(c, pos))
                    self._brackets += 1
                    pos += 1
                    continue
            if c == '}':
                # try to register this closing where it opens.
                try:
                    open_idx = self._stack_bracket[-1]
                    self._words[open_idx].close_macro(self._index - open_idx)
                    self._stack_bracket.pop()
                except IndexError:
                    # Word not entered in Words wordlist or it has no macro.
                    # Register on current word macro if it exists.
                    if word.macros:
                        word.close_macro(0)
                        self._stack_bracket.pop()
                self._brackets -= 1
                word.suffixes.append(Element(c, pos))
                pos += 1
                continue
            if c == '%':
                lb = string[pos:].find('\n')
                if lb is not -1:
                    line = string[pos:pos + lb + 1]
                else:
                    line = string[pos:]
                word.comment.append(Element(line, pos))
                pos += len(line)
                continue
            if re.match(r'[\U00000020-\U0010FFFF]', c):
                # Matches ANY unicode codepoint and registers it.
                word.content.append(Element(c, pos))
                pos += 1
                continue

        return word, pos
