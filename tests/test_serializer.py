import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from invoiceline import LineItem, format_item, format_items, parse


def _item(**overrides):
    base = LineItem(
        quantity=Decimal("3"),
        description="Widget bracket",
        unit_price=Decimal("12.50"),
        currency="USD",
        line=1,
    )
    return replace(base, **overrides)


class FormatItemTests(unittest.TestCase):
    def test_basic_item(self):
        self.assertEqual(format_item(_item()), "3 x Widget bracket @ 12.50 USD")

    def test_discount_and_tax(self):
        item = _item(discount=Decimal("10"), tax_rate=Decimal("8.5"))
        self.assertEqual(
            format_item(item),
            "3 x Widget bracket @ 12.50 USD discount 10% tax 8.5%",
        )

    def test_tax_only(self):
        item = _item(tax_rate=Decimal("8"))
        self.assertEqual(format_item(item), "3 x Widget bracket @ 12.50 USD tax 8%")

    def test_exponent_decimals_are_written_positionally(self):
        item = _item(quantity=Decimal("1E+2"), unit_price=Decimal("5E-2"))
        self.assertEqual(format_item(item), "100 x Widget bracket @ 0.05 USD")

    def test_currency_is_uppercased(self):
        self.assertTrue(format_item(_item(currency="eur")).endswith("@ 12.50 EUR"))

    def test_description_is_stripped(self):
        self.assertEqual(
            format_item(_item(description="  Widget  ")), "3 x Widget @ 12.50 USD"
        )

    def test_rejects_at_sign_in_description(self):
        with self.assertRaises(ValueError):
            format_item(_item(description="a @ b"))

    def test_rejects_empty_description(self):
        with self.assertRaises(ValueError):
            format_item(_item(description="   "))

    def test_rejects_newline_in_description(self):
        with self.assertRaises(ValueError):
            format_item(_item(description="two\nlines"))

    def test_rejects_bad_currency(self):
        with self.assertRaises(ValueError):
            format_item(_item(currency="EURO"))


class RoundTripTests(unittest.TestCase):
    def test_parse_format_parse_is_stable(self):
        source = "\n".join(
            [
                "3 x Widget bracket @ 12.50",
                "1 x On-site consulting hour @ 150 EUR discount 10%",
                "2 x Replacement cable @ 4.99 tax 8%",
                "1.5 x Fabric x2 @ 20 GBP discount 5% tax 20%",
            ]
        )
        items = parse(source)
        again = parse(format_items(items))
        self.assertEqual(again, items)

    def test_format_items_ends_each_line_with_newline(self):
        text = format_items([_item(), _item(description="Other")])
        self.assertEqual(
            text, "3 x Widget bracket @ 12.50 USD\n3 x Other @ 12.50 USD\n"
        )

    def test_format_items_empty(self):
        self.assertEqual(format_items([]), "")


if __name__ == "__main__":
    unittest.main()
