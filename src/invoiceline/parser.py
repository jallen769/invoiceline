"""Parser for the invoiceline plain-text line item format.

One line item per line:

    <quantity> x <description> @ <unit price> [currency]

Blank lines and lines starting with '#' are ignored. Currency defaults to
USD when omitted.
"""

import re
from decimal import Decimal
from typing import List

from .errors import ParseError
from .models import LineItem

_NUMBER = re.compile(r"-?\d+(\.\d+)?")
_CURRENCY = re.compile(r"[A-Za-z]{3}")


def parse(source: str) -> List[LineItem]:
    items = []
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        items.append(_parse_line(raw_line, line_no, source))
    return items


def _parse_line(text: str, line_no: int, source: str) -> LineItem:
    pos = _skip_ws(text, 0)

    match = _NUMBER.match(text, pos)
    if not match:
        raise ParseError("expected a quantity number", source, line_no, pos + 1)
    quantity = Decimal(match.group())
    if quantity <= 0:
        raise ParseError("quantity must be greater than zero", source, line_no, pos + 1)
    pos = match.end()

    pos = _skip_ws(text, pos)
    is_x = text[pos : pos + 1] == "x" and not (
        pos + 1 < len(text) and text[pos + 1].isalnum()
    )
    if not is_x:
        raise ParseError("expected 'x' after quantity", source, line_no, pos + 1)
    pos += 1

    pos = _skip_ws(text, pos)
    at_index = text.find("@", pos)
    if at_index == -1:
        raise ParseError("expected '@' before the unit price", source, line_no, len(text) + 1)

    description = text[pos:at_index].strip()
    if not description:
        raise ParseError(
            "expected a description between 'x' and '@'", source, line_no, pos + 1
        )

    pos = at_index + 1
    pos = _skip_ws(text, pos)
    match = _NUMBER.match(text, pos)
    if not match:
        raise ParseError("expected a unit price after '@'", source, line_no, pos + 1)
    unit_price = Decimal(match.group())
    pos = match.end()

    pos = _skip_ws(text, pos)
    currency = "USD"
    if pos < len(text):
        match = _CURRENCY.match(text, pos)
        if not match:
            raise ParseError(
                "expected a 3-letter currency code", source, line_no, pos + 1
            )
        currency = match.group().upper()

    return LineItem(
        quantity=quantity,
        description=description,
        unit_price=unit_price,
        currency=currency,
        line=line_no,
    )


def _skip_ws(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] in " \t":
        pos += 1
    return pos
