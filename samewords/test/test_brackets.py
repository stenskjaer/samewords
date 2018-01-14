from samewords.brackets import Brackets

class TestBrackets:

    def test_single_bracket(self):
        text = r'{bracket without anything} but following text'
        bracks = Brackets(text)
        assert len(bracks) == 26
        assert bracks.content() == '{bracket without anything}'

    def test_with_one_nested_bracket(self):
        text = r'{bracket \emph{with} another} and following text'
        bracks = Brackets(text)
        assert len(bracks) == 29
        assert bracks.content() == '{bracket \emph{with} another}'

    def test_with_two_nested_bracket(self):
        text = r'{bracket \emph{with \emph{more}} than one} and following text'
        bracks = Brackets(text)
        assert len(bracks) == 42
        assert bracks.content() == '{bracket \emph{with \emph{more}} than one}'

    def test_two_sequential_nested_brackets(self):
        text = r'{bracket \emph{one} and \emph{two} inside} and following text'
        bracks = Brackets(text)
        assert len(bracks) == 42
        assert bracks.content() == '{bracket \emph{one} and \emph{two} inside}'

    def test_with_escaped_brackets(self):
        text = r'{bracket \{ and \} \{ \{ inside} and following text'
        bracks = Brackets(text)
        assert len(bracks) == 32
        assert bracks.content() == '{bracket \{ and \} \{ \{ inside}'

