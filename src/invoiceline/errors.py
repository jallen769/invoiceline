"""Error type for the invoiceline parser.

The whole point of this module is that a ParseError should be as easy to
act on as a compiler error: which line, which column, and a caret pointing
at the exact spot, not just "invalid line item".
"""


class ParseError(Exception):
    def __init__(self, message: str, source: str, line: int, column: int):
        self.message = message
        self.source = source
        self.line = line
        self.column = column
        super().__init__(self._render())

    def _render(self) -> str:
        lines = self.source.splitlines()
        text = lines[self.line - 1] if 0 < self.line <= len(lines) else ""
        # Expand tabs to a single space so the caret still lines up under
        # the offending character regardless of the reader's tab width.
        clean = text.replace("\t", " ")
        caret = " " * max(self.column - 1, 0) + "^"
        return (
            f"line {self.line}, column {self.column}: {self.message}\n"
            f"    {clean}\n"
            f"    {caret}"
        )
