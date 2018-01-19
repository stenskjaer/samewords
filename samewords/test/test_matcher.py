from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
from samewords import cli


class TestMatcher:

    def test_no_match_single_level(self):
        text = 'text \edtext{emphasis}{\Bfootnote{fnote}} is nice'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        assert matcher.context_match(tokenization.registry[0]) == False

    def test_match_single_level(self):
        text = 'emphasis \edtext{emphasis}{\Bfootnote{fnote}} is nice'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        assert matcher.context_match(tokenization.registry[0]) == True
class TestSamewordWrapper:

    def test_wrap_unwrapped_sameword(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 0, level=1)
        assert matcher.words.write() == r'\sameword[1]{sw}'

    def test_wrap_multiword(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 3, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'

    def test_wrap_wrapped_sameword_without_argument(self):
        text = r'\sameword{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 0, level=2)
        assert matcher.words.write() == r'\sameword[2]{sw}'

    def test_wrap_wrapped_multiword_without_argument(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 3, level=2)
        assert matcher.words.write() == r'\sameword[2]{one word and another}'

    def test_wrap_wrapped_sameword_with_argument(self):
        text = r'\sameword[2]{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 0, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{sw}'

    def test_wrap_wrapped_multiword_with_argument(self):
        text = r'\sameword[2]{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 3, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{one word and another}'

    def test_wrap_no_lemma(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 0, level=0)
        assert matcher.words.write() == r'\sameword{sw}'

    def test_wrap_multiword_no_lemma(self):
        text = r'one word and another'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(0, 3, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'


class TestDefineSearchWords:

    def run_wordlist(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        return matcher._define_search_words(tokenization.wordlist)

    def test_single_lemma_word(self):
        text = '\edtext{item}{\lemma{item}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item']

    def test_multiword_lemma_first(self):
        text = '\edtext{item and more}{\lemma{item and more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item', 'and', 'more']

    def test_ellipsis_lemma_first(self):
        text = '\edtext{one a b c more}{\lemma{one ... more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['one', 'more']

    def test_single_no_lemma(self):
        text = '\edtext{item}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item']

    def test_multiword_no_lemma(self):
        text = '\edtext{item and more}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item', 'and', 'more']

    def test_custom_ellipsis_dots(self):
        fname = './samewords/test/assets/sample_config.json'
        cli.parse_config_file(fname)
        single_dash = r'\edtext{A B C D E}{\lemma{A - E}\Afootnote{}}'
        double_dash = r'\edtext{A B C D E}{\lemma{A -- E}\Afootnote{}}'
        triple_dash = r'\edtext{A B C D E}{\lemma{A --- E}\Afootnote{}}'
        endash = r'\edtext{A B C D E}{\lemma{A – E}\Afootnote{}}'
        emdash = r'\edtext{A B C D E}{\lemma{A — E}\Afootnote{}}'
        comma_string = r'\edtext{A B C D E}{\lemma{A ,-, E}\Afootnote{}}'
        thin_space = r'\edtext{A B C D E}{\lemma{A\,--\,E}\Afootnote{}}'
        dots = r'\edtext{A B C D E}{\lemma{A \dots E}\Afootnote{}}'
        dots_brackets = r'\edtext{A B C D E}{\lemma{A \dots{} E}\Afootnote{}}'
        ldots = r'\edtext{A B C D E}{\lemma{A \ldots E}\Afootnote{}}'
        ldots_brackets = r'\edtext{A B C D E}{\lemma{A \ldots{} E}\Afootnote{}}'
        expect = ['A', 'E']
        assert self.run_wordlist(single_dash) == expect
        assert self.run_wordlist(double_dash) == expect
        assert self.run_wordlist(triple_dash) == expect
        assert self.run_wordlist(endash) == expect
        assert self.run_wordlist(emdash) == expect
        assert self.run_wordlist(comma_string) == expect
        assert self.run_wordlist(thin_space) == expect
        assert self.run_wordlist(dots) == expect
        assert self.run_wordlist(dots_brackets) == expect
        assert self.run_wordlist(ldots) == expect
        assert self.run_wordlist(ldots_brackets) == expect
