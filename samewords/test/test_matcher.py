from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
from samewords import cli


class TestMatcher:

    def run_annotation(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        words = matcher.annotate()
        return words.write()

    def test_no_match_single_level(self):
        text = r'text \edtext{emphasis}{\Bfootnote{fnote}} is nice'
        assert self.run_annotation(text) == text

    def test_match_single_level_single_item(self):
        text = r'emphasis \edtext{emphasis}{\Bfootnote{fnote}} is emphasis'
        expect = r'\sameword{emphasis} \edtext{\sameword[1]{emphasis}}{\Bfootnote{fnote}} is \sameword{emphasis}'
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiple_context_matches(self):
        text = r'emphasis a emphasis \edtext{emphasis}{\Bfootnote{fnote}} and emphasis'
        expect = r'\sameword{emphasis} a \sameword{emphasis} \edtext{\sameword[1]{emphasis}}{\Bfootnote{fnote}} and \sameword{emphasis}'
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword(self):
        text = r'\sameword{a b} and a b \edtext{a b}{\Bfootnote{fnote}} a b and a b'
        expect = r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a b}}{\Bfootnote{fnote}} \sameword{a b} and \sameword{a b}'
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword_lemma(self):
        text = r'\sameword{a b} and a b \edtext{a b}{\lemma{a b}\Bfootnote{fnote}} a b and a b'
        expect = r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a b}}{\lemma{a b}\Bfootnote{fnote}} \sameword{a b} and \sameword{a b}'
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword_lemma_ellipsis(self):
        text = r'\sameword{a} b and c \edtext{a and c}{\lemma{a \dots{} c}\Bfootnote{fnote}} and c and c'
        expect = r'\sameword{a} b and \sameword{c} \edtext{\sameword[1]{a and c}}{\lemma{a \dots{} c}\Bfootnote{fnote}} and \sameword{c} and \sameword{c}'
        assert self.run_annotation(text) == expect

    def test_three_close_nested_levels(self):
        text = (r"so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev "
                r"3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev"
                r" 1}}")
        expect = (r"\sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,"
                  r"3]{so}}{\lemma{so}\Bfootnote{lev 3}}}{\lemma{"
                  r"so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev "
                  r"1}}")
        assert self.run_annotation(text) == expect


class TestSamewordWrapper:

    def test_wrap_unwrapped_sameword(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1]{sw}'

    def test_wrap_multiword(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'

    def test_wrap_wrapped_sameword_without_argument(self):
        text = r'\sameword{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=2)
        assert matcher.words.write() == r'\sameword[2]{sw}'

    def test_wrap_wrapped_multiword_without_argument(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=2)
        assert matcher.words.write() == r'\sameword[2]{one word and another}'

    def test_wrap_wrapped_sameword_with_argument(self):
        text = r'\sameword[2]{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{sw}'

    def test_wrap_wrapped_multiword_with_argument(self):
        text = r'\sameword[2]{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{one word and another}'

    def test_wrap_no_lemma(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{sw}'

    def test_wrap_multiword_no_lemma(self):
        text = r'one word and another'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'

    def test_wrap_multi_partially_wrapped(self):
        text = r'input \sameword{material}'
        expect = r'\sameword{input \sameword{material}}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == expect

    def test_wrap_multi_both_wrapped(self):
        text = r'\sameword{input} \sameword{material}'
        expect = r'\sameword[1]{\sameword{input} \sameword{material}}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == expect


class TestDefineSearchWords:

    def run_wordlist(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        return matcher._define_search_words(tokenization.wordlist)

    def test_single_lemma_word(self):
        text = '\edtext{item}{\lemma{item}\Bfootnote{fnote}}'
        assert self.run_wordlist(text).content == ['item']

    def test_multiword_lemma_first(self):
        text = '\edtext{item and more}{\lemma{item and more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text).content == ['item', 'and', 'more']

    def test_ellipsis_lemma_first(self):
        text = '\edtext{one a b c more}{\lemma{one ... more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text).content == ['one', 'more']

    def test_single_no_lemma(self):
        text = '\edtext{item}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text).content == ['item']

    def test_multiword_no_lemma(self):
        text = '\edtext{item and more}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text).content == ['item', 'and', 'more']

    def test_nested_multiwords_no_lemma(self):
        """Simulate the annotation procedure by getting the search word
        results for each nested level """
        text = r"""
            \edtext{lvl1 \edtext{lvl2 \edtext{lvl3-1}{\Bfootnote{n3}} inter
            \edtext{lvl3-2}{\Bfootnote{n4}}}{\Bfootnote{n2}}}{\Bfootnote{n1}}
            """
        expect = [['lvl1', 'lvl2', 'lvl3-1', 'inter', 'lvl3-2'],
                  ['lvl2', 'lvl3-1', 'inter', 'lvl3-2'],
                  ['lvl3-1'], ['lvl3-2']]
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        search_words = []
        for entry in matcher.registry:
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = matcher.words[edtext_start:edtext_end + 1]
            search_words.append(matcher._define_search_words(edtext).content)
        assert search_words == expect

    def test_nested_multiwords_with_lemma(self):
        """Simulate the annotation procedure by getting the search word
        results for each nested level """
        text = r"""
            \edtext{lvl1 \edtext{lvl2 \edtext{lvl3-1}{\lemma{l3}\Bfootnote{n3}} 
            inter
            \edtext{lvl3-2}{\lemma{l4}\Bfootnote{n4}}}{\lemma{l2}\Bfootnote{n2}}}{\lemma{l1}\Bfootnote{n1}}
            """
        expect = [['l1'], ['l2'], ['l3'], ['l4']]
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        search_words = []
        for entry in matcher.registry:
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = matcher.words[edtext_start:edtext_end + 1]
            search_words.append(matcher._define_search_words(edtext).content)
        assert search_words == expect

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
        assert self.run_wordlist(single_dash).content == expect
        assert self.run_wordlist(double_dash).content == expect
        assert self.run_wordlist(triple_dash).content == expect
        assert self.run_wordlist(endash).content == expect
        assert self.run_wordlist(emdash).content == expect
        assert self.run_wordlist(comma_string).content == expect
        assert self.run_wordlist(thin_space).content == expect
        assert self.run_wordlist(dots).content == expect
        assert self.run_wordlist(dots_brackets).content == expect
        assert self.run_wordlist(ldots).content == expect
        assert self.run_wordlist(ldots_brackets).content == expect
