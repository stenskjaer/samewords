import re
import string

from collections import UserString, UserList
from typing import List, Tuple


class Macro(UserString):
    """A latex macro, holding information in its name and optional arguments.
    """

    def __init__(self, input_string: str = '') -> None:
        self.data = input_string
        super().__init__(self)
        self.name = self._identify_name()
        self.oarg = self._optional_argument()
        self.empty = self._is_empty()
        self.complete = self._full()

    def __len__(self) -> int:
        return len(self.complete)

    def __repr__(self) -> str:
        return "'{}'".format(self.complete)

    def __str__(self) -> str:
        return str(self.complete)

    def _identify_name(self) -> str:
        """
        A TeX macro can be '\' followed by either a string of letters or
        any single character. Find that.
        """
        return re.match(r'\\(\w+|.)', self.data).group(0)

    def _optional_argument(self) -> str:
        """
        Identify the possible optinal argument of the marco.
        """
        match = re.match(r'\\[^ ]+(\[[^\]]+\])', self.data)
        if match:
            return match.group(1)
        return ''

    def _is_empty(self) -> bool:
        """
        If the macro contains an opening bracket that is not followed
        immediately by a closing bracket, it has some content.
        """
        opening = re.match(r'\\[^ ]+{', self.data)
        if opening:
            if not(self.data[len(opening.group(0))] == '}'):
                return False
        return True

    def _full(self) -> str:
        opening = re.match(r'[^ ]+?{', self.data)
        if opening:
            return opening.group(0)
        else:
            return self.name



class Word(UserString):

    def __init__(self, chars: str = '') -> None:
        self.data = chars
        super().__init__(self)
        self.text = ''
        self.spaced = False
        self.spaces = ''
        self.prefix = []
        self.suffix = []
        self.macro = ''

    def __str__(self) -> str:
        return str(self.text)

    def __repr__(self) -> str:
        return "'{}'".format(self.text)

    def __eq__(self, other) -> bool:
        return self.text == other

    def full(self) -> str:
        """
        :return: full word including prefix and suffix.
        """
        pref = ''.join(self.prefix)
        suff = ''.join(self.suffix)
        return pref + str(self.macro) + self.text + suff + self.spaces


class Words(UserList):

    def write(self) -> str:
        return ''.join([w.full() for w in self.data])


class Tokenizer:
    in_crit = False
    in_app = False
    edtext_lvl = 0
    brackets = 0
    open_stack = []
    punctuation = re.compile('[{}]+'.format(string.punctuation))
    edtext_brackets = []

    def __init__(self, input: str = '') -> None:
        """
        self.edtext_brackets: registry of opened brackets at the beginning of
        each edtext macro. Each integer corresponds to a higher level of
        nested edtexts. When a } is hit and the edtext_brackets of that level
        is reached, the encountered } closes the edtext.

        :param input: The input string that will be tokenized.
        """
        self.data = input
        self.registry = []
        self.wordlist = self._wordlist()

    def _wordlist(self) -> Words:
        words = Words()
        pos = 0
        while pos < len(self.data):
            word, pos = self._tokenize(self.data, pos)
            words.append(word)
            index = len(words)
            if word.macro:
                if word.macro.name == r'\edtext':
                    # Opening an edtext macro.
                    self.open_stack.append(len(self.registry))
                    self.edtext_lvl += 1
                    self.registry.append(
                        {'lvl': self.edtext_lvl, 'data': [index]}
                    )
                    self.edtext_brackets.insert(self.edtext_lvl, self.brackets)
                self.brackets += 1
            if '{' in word.prefix:
                # Opening bracket
                self.brackets += ''.join(word.prefix).count('{')
                if '}' in words[index-1].suffix:
                    # Is the opening bracket preceded by closing bracket?
                    # Then we are in the second argument of a macro.
                    # TODO: (false) Assumption that this is an edtext app note.
                    self.registry[self.open_stack[-1]]['data'].append(index)
                    self.in_app = True
            if '}' in word.suffix:
                # Closing bracket
                self.brackets -= ''.join(word.suffix).count('}')
                if self.in_app:
                    # Are we in apparatus note?
                    if self.brackets == self.edtext_brackets[self.edtext_lvl-1]:
                        # Have all brackets inside the app note been closed?
                        # In that case, we close the registry, pop the
                        # stacks, close the app and decrement the edtext level.
                        self.registry[self.open_stack[-1]]['data'].append(index)
                        self.edtext_brackets.pop()
                        self.open_stack.pop()
                        self.in_app = False
                        self.edtext_lvl -= 1
        return words

    def _tokenize(self, string: str, pos: int = 0) -> Tuple[Word, int]:
        """
        Idea: Run the string and build a Word object. Collect characters,
        digits and hyphens into word.text property. Punctuation goes into
        prefix and suffix properties. Macros enclosing the Word.text are put
        in the Word.macro property.
        """
        word = Word()
        while pos < len(string):
            c = string[pos]
            if re.match('[\w\d]', string[pos]):
                if '}' in word.suffix:
                    #  Word already has closing brackets, so start a new word
                    break
                match = re.match('[\w\d-]+', string[pos:]).group(0)
                word.text += match
                pos += len(match)
                continue
            if c == '\\':
                if word.text:
                    # No appended macros
                    break
                macro = Macro(string[pos:])
                word.macro = macro
                pos += len(macro)
                if macro.empty and not(string[pos].isspace()):
                    # Empty macros cannot have following chars (e.g. A\,B)
                    break
                continue
            if re.search(self.punctuation, c):
                # Exception: .5 is part of word, not punctuation.
                if re.match('\.\d', string[pos:]):
                    word.text += c
                    pos += 1
                    continue
                if word.text:
                    if c == '{':
                        break
                    word.suffix.append(c)
                else:
                    word.prefix.append(c)
                pos += 1
                continue
            if c.isspace():
                word.spaced = True
                word.spaces = re.match('\s+', string[pos:]).group(0)
                pos += len(word.spaces)
                break

        return word, pos
