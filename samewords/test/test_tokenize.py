import re

from samewords.tokenize import Tokenizer
from samewords.test.assets.unicode_register import blocks
from samewords.settings import settings

class TestTokenize:

    def write_tokenization(self, input_text):
        return Tokenizer(input_text).wordlist.write()

    def test_unicode_blocks(self):
        for block in blocks:
            # Test the last point in each block
            point = chr(int(blocks[block][1], 16))
            if not re.match(r'[{}]+'.format(''.join(settings['punctuation'])),
                            point):
                assert Tokenizer(point).wordlist == [point]

    def test_whitespace(self):
        text = 'short text\t with    some\n space and stuff'
        expect = ['short', 'text', 'with', 'some', 'space', 'and', 'stuff']
        assert Tokenizer(text).wordlist == expect
        assert Tokenizer(text).wordlist.write() == text

    def test_single_macro(self):
        text = 'text \emph{emphasis} is nice'
        expect = ['text', 'emphasis', 'is', 'nice']
        tokens = Tokenizer(text)
        assert tokens.wordlist == expect
        assert tokens.wordlist.write() == text

    def test_nested_macro(self):
        text = r'text \emph{with \textbf{nesting} emphasis}'
        expect = ['text', 'with', 'nesting', 'emphasis']
        tokens = Tokenizer(text)
        assert tokens.wordlist == expect
        assert tokens.wordlist.write() == text

    def test_registry(self):
        text = 'text \edtext{emphasis}{\Bfootnote{fnote}} is nice'
        expect = ['text', 'emphasis', 'is', 'nice']
        registry = [{'lvl': 0, 'data': [1, 1]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == expect
        assert tokenization.wordlist.write() == text
        assert tokenization.registry == registry

    def test_edtext_with_nested_brackets(self):
        text = '\edtext{entry \emph{nested \emph{b}}}{\Bfootnote{fnote}} nice'
        expect = ['entry', 'nested', 'b', 'nice']
        registry = [{'lvl': 0, 'data': [0, 2]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == expect
        assert tokenization.wordlist.write() == text
        assert tokenization.registry == registry

    def test_tokenizer_two_levels(self):
        text = r"""
        \edtext{lvl1 \edtext{lvl2 }{\Bfootnote{l2-note}}}{\Bfootnote{l1-note}}
        """
        expect = ['', 'lvl1', 'lvl2', '']
        registry = [{'lvl': 0, 'data': [1, 3]}, {'lvl': 1, 'data': [2, 3]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == expect
        assert tokenization.wordlist.write() == text
        assert tokenization.registry == registry

    def test_registry_with_nesting_and_sequential_nested_entries(self):
        text = r"""
        \edtext{lvl1 \edtext{lvl2 \edtext{lvl3-1}{\Bfootnote{n3}} inter
        \edtext{lvl3-2}{\Bfootnote{n4}}}{\Bfootnote{n2}}}{\Bfootnote{n1}}
        """
        expect = ['', 'lvl1', 'lvl2', 'lvl3-1', 'inter', 'lvl3-2']
        registry = [{'lvl': 0, 'data': [1, 5]},
                    {'lvl': 1, 'data': [2, 5]},
                    {'lvl': 2, 'data': [3, 3]},
                    {'lvl': 2, 'data': [5, 5]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == expect
        assert tokenization.wordlist.write() == text
        assert tokenization.registry == registry

    def test_registry_with_three_close_levels(self):
        text = (r"so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev "
                r"3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev"
                r" 1}}")
        expect = ['so', 'so']
        registry = [{'lvl': 0, 'data': [1, 1]},
                    {'lvl': 1, 'data': [1, 1]},
                    {'lvl': 2, 'data': [1, 1]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == expect
        assert tokenization.registry == registry
        assert tokenization.wordlist.write() == text

    def test_edtext_by_another_edtext_are_separated(self):
        text = r"\edtext{a}{\Bfootnote{b}},\edtext{c}{\Bfootnote{d}}"
        wordlist = ['a', 'c']
        registry = [{'lvl': 0, 'data': [0, 0]}, {'lvl': 0, 'data': [1, 1]}]
        tokenization = Tokenizer(text)
        assert tokenization.wordlist == wordlist
        assert tokenization.registry == registry
        assert tokenization.wordlist.write() == text

    def test_space_macros(self):
        thinspace1 = r'A\,B'
        thinspace2 = r'A\thinspace B'
        enskip = r'A\enskip B'
        quad = r'A\quad B'
        qquad = r'A\qquad B'
        hskip = r'A\hskip{10pt}B'
        enspace = r'A\enspace B'
        negthinspace = r'A\negthinspace B'
        kern = r'A\kern{.5em}B'
        non_spaced_result = ['A', 'B']
        spaced_result = ['A', '', 'B']
        assert Tokenizer(thinspace1).wordlist == non_spaced_result
        assert Tokenizer(thinspace2).wordlist == spaced_result
        assert Tokenizer(enskip).wordlist == spaced_result
        assert Tokenizer(quad).wordlist == spaced_result
        assert Tokenizer(qquad).wordlist == spaced_result
        assert Tokenizer(hskip).wordlist == ['A', 'B']
        assert Tokenizer(enspace).wordlist == spaced_result
        assert Tokenizer(negthinspace).wordlist == spaced_result
        assert Tokenizer(kern).wordlist == ['A', 'B']

        assert Tokenizer(thinspace1).wordlist.write() == thinspace1
        assert Tokenizer(thinspace2).wordlist.write() == thinspace2
        assert Tokenizer(enskip).wordlist.write() == enskip
        assert Tokenizer(quad).wordlist.write() == quad
        assert Tokenizer(qquad).wordlist.write() == qquad
        assert Tokenizer(hskip).wordlist.write() == hskip
        assert Tokenizer(enspace).wordlist.write() == enspace
        assert Tokenizer(negthinspace).wordlist.write() == negthinspace
        assert Tokenizer(kern).wordlist.write() == kern

    def test_punctuation(self):
        text = 'text, with. punctuation.-!"#$&()*+,-./:;<=>?@[]^`|~ enough?!'
        expect = ['text', 'with', 'punctuation', 'enough']
        tokens = Tokenizer(text)
        assert tokens.wordlist == expect
        assert tokens.wordlist.write() == text

    def test_punctuation_location(self):
        before_macro = r'.,|\macro{Content}'
        before_word = r'\macro{.,|Content}'
        after_word = r'\macro{Content.,|}'
        after_simple_macro = r'\macro{Content}.,|'
        after_empty_macro = r'Apostolus\index[persons]{}},'
        after_edtext_macro = r'\edtext{Content}{\Bfoofnote{xxx}}.,|'
        mixed = r'|\edtext{.Content|}{\Bfoofnote{xxx}}.,|'
        before_no_macro = r'.Hello'
        after_no_macro = r'Hello|'
        assert self.write_tokenization(before_macro) == before_macro
        assert self.write_tokenization(before_word) == before_word
        assert self.write_tokenization(after_word) == after_word
        assert self.write_tokenization(after_simple_macro) == after_simple_macro
        assert self.write_tokenization(after_empty_macro) == after_empty_macro
        assert self.write_tokenization(after_edtext_macro) == after_edtext_macro
        assert self.write_tokenization(mixed) == mixed
        assert self.write_tokenization(before_no_macro) == before_no_macro
        assert self.write_tokenization(after_no_macro) == after_no_macro

    def test_words_with_integrated_macros(self):
        text = (r'Hákon\emph{ar}')
        assert self.write_tokenization(text) == text

    def test_word_with_multiple_integrated_macros(self):
        text = (r'Seg\emph{men}ta\emph{tion}')
        assert self.write_tokenization(text) == text
