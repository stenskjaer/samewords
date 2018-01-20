from samewords.tokenize import Tokenizer

from pytest import mark

class TestTokenize:

    def test_whitespace(self):
        text = 'short text\t with    some\n space and stuff'
        expect = ['short', 'text', 'with', 'some', 'space', 'and', 'stuff']
        assert Tokenizer(text).wordlist == expect
        assert Tokenizer(text).wordlist.write() == text

    def test_punctuation(self):
        text = 'text, with. punctuation.-!"#$%&()*+,-./:;<=>?@[]^`|~ enough?!'
        expect = ['text', 'with', 'punctuation', 'enough']
        tokens = Tokenizer(text)
        assert tokens.wordlist == expect
        assert tokens.wordlist.write() == text

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
        result = ['A', '', 'B']
        assert Tokenizer(thinspace1).wordlist == result
        assert Tokenizer(thinspace2).wordlist == result
        assert Tokenizer(enskip).wordlist == result
        assert Tokenizer(quad).wordlist == result
        assert Tokenizer(qquad).wordlist == result
        assert Tokenizer(hskip).wordlist == ['A', '10pt', 'B']
        assert Tokenizer(enspace).wordlist == result
        assert Tokenizer(negthinspace).wordlist == result
        assert Tokenizer(kern).wordlist == ['A', '.5em', 'B']

        assert Tokenizer(thinspace1).wordlist.write() == thinspace1
        assert Tokenizer(thinspace2).wordlist.write() == thinspace2
        assert Tokenizer(enskip).wordlist.write() == enskip
        assert Tokenizer(quad).wordlist.write() == quad
        assert Tokenizer(qquad).wordlist.write() == qquad
        assert Tokenizer(hskip).wordlist.write() == hskip
        assert Tokenizer(enspace).wordlist.write() == enspace
        assert Tokenizer(negthinspace).wordlist.write() == negthinspace
        assert Tokenizer(kern).wordlist.write() == kern
