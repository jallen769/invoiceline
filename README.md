# invoiceline

A small library for parsing invoice line items out of plain text.

The use case: someone pastes a handful of line items into a text box, or a
line item file gets hand-edited, and something is off - a missing `@`, a
quantity that isn't a number, a currency code that got mistyped. Most
parsers for this kind of thing just raise `ValueError: invalid line item`
and leave you to find the problem yourself. This one tells you exactly
where to look.

## Format

One line item per line:

```
<quantity> x <description> @ <unit price> [currency] [discount N%] [tax N%]
```

Currency defaults to `USD` if omitted. `discount` and `tax`, when present,
must appear in that order; both are percentages applied to the line
subtotal, discount first, then tax on the discounted amount. Blank lines
and lines starting with `#` are ignored.

```
# March consulting
3 x Widget bracket @ 12.50
1 x On-site consulting hour @ 150 EUR discount 10%
2 x Replacement cable @ 4.99 tax 8%
```

## Usage

```python
from invoiceline import parse

source = """
3 x Widget bracket @ 12.50
1 x On-site consulting hour @ 150 EUR
"""

items = parse(source)
for item in items:
    print(item.line, item.description, item.total, item.currency)
```

## Errors

When a line can't be parsed, `parse` raises `ParseError` with the exact
line and column of the problem, plus a caret pointing at it:

```python
from invoiceline import parse, ParseError

try:
    parse("3 x Widget bracket 12.50")
except ParseError as err:
    print(err)
```

```
line 1, column 20: expected '@' before the unit price
    3 x Widget bracket 12.50
                       ^
```

`ParseError` also exposes `.line`, `.column`, and `.message` separately, so
callers building their own UI don't have to parse the rendered string back
apart.

## Status

Early. The format covers quantity, description, unit price, currency,
discount, and tax rate. Still missing: multi-currency invoice totals, a
serialize/format function to round-trip a `LineItem` back to text, and
quoted descriptions for when the description itself contains `@` or `x`.
See the issue tracker for what's planned.

## License

MIT, see LICENSE.
