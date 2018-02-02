from samewords.tokenize import Macro


class TestMacro:

    def test_simple_macro(self):
        text = '\emph{content} and something more'
        m = Macro(text)
        assert m.full() == r'\emph{'
        assert m.name == r'\emph'

    def test_optional_argument(self):
        text = '\macro[optional]{content}'
        m = Macro(text)
        assert m.full() == r'\macro[optional]{'
        assert m.name == r'\macro'
        assert m.oarg == r'[optional]'

    def test_unbracketed_macro(self):
        text = '\macro and then some more text'
        m = Macro(text)
        assert m.full() == r'\macro'
        assert m.name == r'\macro'
        assert m.empty == True

    def test_single_char_macro(self):
        text = '\, and then some more text'
        m = Macro(text)
        assert m.full() == r'\,'
        assert m.name == r'\,'
        assert m.empty == True

    def test_empty_bracketed_macro(self):
        text = '\macro{} and more text'
        m = Macro(text)
        assert m.full() == r'\macro{'
        assert m.name == r'\macro'
        assert m.empty == True

    def test_close_macro_with_linebreak(self):
        text = '\\pstart\ntest\nthirtieth'
        m = Macro(text)
        assert m.full() == r'\pstart'
        assert m.name == r'\pstart'
        assert m.empty == True
