
class Brackets:
    """
    Given a start position with a bracket, analyze the length and make the
    content available.
    """

    def __init__(self, search_string: str, start: int = 0) -> None:
        self.data = search_string
        self.start = start
        self.end = self._find_end(self.start)

    def __len__(self):
        return self.end - self.start

    def _find_end(self, pos: int = 0, opened: int = 0, end: int = 0) -> int:
        """Find the end position of the bracket.
        """
        if self.data[pos] == '{':
            opened = 1
            pos += 1
            while opened > 0:
                c = self.data[pos]
                if c == '\\':
                    pos += 2
                    continue
                if c == '{':
                    opened += 1
                elif c == '}':
                    opened -= 1
                pos += 1
            return pos
        else:
            raise ValueError("The bracket is not closed:\n"
                             "%s" % self.data[self.start:self.start+50])

    def content(self):
        return self.data[self.start:self.end]

