"""Turn LineItem objects back into the plain-text line item format."""

from decimal import Decimal
from typing import Iterable

from .models import LineItem


def format_item(item: LineItem) -> str:
    """Return the text form of one line item, without a trailing newline.

    Raises ValueError if the item can't be written in a form that parse()
    would read back as the same item.
    """
    description = item.description.strip()
    if not description:
        raise ValueError("description is empty")
    if "@" in description:
        # The parser splits on the first '@', so there is no way to write this.
        raise ValueError("description cannot contain '@'")
    if "\n" in description or "\r" in description:
        raise ValueError("description cannot span multiple lines")
    if len(item.currency) != 3 or not item.currency.isascii() or not item.currency.isalpha():
        raise ValueError("currency must be a 3-letter code: %r" % item.currency)

    parts = [
        "%s x %s @ %s %s"
        % (
            _number(item.quantity),
            description,
            _number(item.unit_price),
            item.currency.upper(),
        )
    ]
    if item.discount is not None:
        parts.append("discount %s%%" % _number(item.discount))
    if item.tax_rate is not None:
        parts.append("tax %s%%" % _number(item.tax_rate))
    return " ".join(parts)


def format_items(items: Iterable[LineItem]) -> str:
    """Return one line per item, each terminated by a newline."""
    return "".join(format_item(item) + "\n" for item in items)


def _number(value: Decimal) -> str:
    # str(Decimal) can produce exponent notation such as '1E+2', which the
    # parser's number pattern does not accept.
    return format(value, "f")
