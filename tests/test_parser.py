import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from invoiceline import ParseError, parse


class ParseSuccessTests(unittest.TestCase):
    def test_minimal_line_defaults_to_usd(self):
        items = parse("3 x Widget bracket @ 12.50")
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.quantity, Decimal("3"))
        self.assertEqual(item.description, "Widget bracket")
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.currency, "USD")
        self.assertEqual(item.line, 1)
        self.assertIsNone(item.discount)
        self.assertIsNone(item.tax_rate)
        self.assertEqual(item.subtotal, Decimal("37.50"))
        self.assertEqual(item.total, Decimal("37.50"))

    def test_explicit_currency_is_uppercased(self):
        item = parse("1 x Consulting hour @ 150 eur")[0]
        self.assertEqual(item.currency, "EUR")

    def test_discount_then_tax(self):
        item = parse("2 x Cable @ 10 USD discount 10% tax 8%")[0]
        self.assertEqual(item.discount, Decimal("10"))
        self.assertEqual(item.tax_rate, Decimal("8"))
        # subtotal 20, minus 10% = 18, plus 8% = 19.44
        self.assertEqual(item.total, Decimal("19.44"))

    def test_discount_only(self):
        item = parse("1 x Widget @ 100 discount 25%")[0]
        self.assertEqual(item.total, Decimal("75.00"))

    def test_tax_only_without_currency(self):
        item = parse("2 x Cable @ 4.99 tax 8%")[0]
        self.assertEqual(item.currency, "USD")
        self.assertEqual(item.tax_rate, Decimal("8"))

    def test_blank_lines_and_comments_are_skipped(self):
        source = "\n".join(
            [
                "# a comment",
                "",
                "3 x Widget @ 1",
                "   ",
                "# another comment",
                "1 x Gadget @ 2",
            ]
        )
        items = parse(source)
        self.assertEqual([item.line for item in items], [3, 6])

    def test_line_numbers_reflect_position_in_source(self):
        source = "1 x First @ 1\n2 x Second @ 2\n3 x Third @ 3"
        items = parse(source)
        self.assertEqual([item.line for item in items], [1, 2, 3])


class ParseErrorTests(unittest.TestCase):
    def assert_error_at(self, source, line, column, message_fragment):
        with self.assertRaises(ParseError) as ctx:
            parse(source)
        err = ctx.exception
        self.assertEqual(err.line, line)
        self.assertEqual(err.column, column)
        self.assertIn(message_fragment, err.message)
        return err

    def test_missing_quantity(self):
        self.assert_error_at("x x Widget @ 5", 1, 1, "expected a quantity number")

    def test_zero_quantity_rejected(self):
        self.assert_error_at("0 x Widget @ 5", 1, 1, "quantity must be greater than zero")

    def test_negative_quantity_rejected(self):
        self.assert_error_at("-1 x Widget @ 5", 1, 1, "quantity must be greater than zero")

    def test_missing_x(self):
        self.assert_error_at("3 Widget @ 5", 1, 3, "expected 'x' after quantity")

    def test_missing_at_sign(self):
        text = "3 x Widget bracket 12.50"
        self.assert_error_at(text, 1, len(text) + 1, "expected '@' before the unit price")

    def test_missing_description(self):
        self.assert_error_at("3 x @ 5", 1, 5, "expected a description between 'x' and '@'")

    def test_missing_unit_price(self):
        self.assert_error_at("3 x Widget @ abc", 1, 14, "expected a unit price after '@'")

    def test_invalid_currency_code(self):
        self.assert_error_at(
            "3 x Widget @ 5 X1", 1, 16, "expected a 3-letter currency code"
        )

    def test_discount_out_of_range(self):
        self.assert_error_at(
            "3 x Widget @ 5 discount 150%", 1, 25, "discount must be between 0 and 100"
        )

    def test_discount_missing_percentage(self):
        self.assert_error_at(
            "3 x Widget @ 5 discount", 1, 24, "expected a percentage after 'discount'"
        )

    def test_negative_tax_rejected(self):
        self.assert_error_at(
            "3 x Widget @ 5 tax -8%", 1, 20, "tax rate cannot be negative"
        )

    def test_tax_before_discount_is_rejected(self):
        # The format requires discount before tax; reversing them leaves
        # 'discount' as unparsed trailing text once 'tax' has been consumed.
        self.assert_error_at(
            "3 x Widget @ 5 tax 8% discount 10%",
            1,
            23,
            "unexpected text after line item",
        )

    def test_trailing_garbage(self):
        self.assert_error_at(
            "3 x Widget @ 5 USD extra", 1, 20, "unexpected text after line item"
        )

    def test_error_message_includes_caret(self):
        err = self.assert_error_at("3 Widget @ 5", 1, 3, "expected 'x' after quantity")
        lines = str(err).splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[1], "    3 Widget @ 5")
        # the rendered source line is indented by 4 spaces, so the caret
        # should land at column - 1 characters after that indent
        self.assertEqual(lines[2].index("^"), 4 + err.column - 1)

    def test_error_points_at_correct_line_in_multiline_source(self):
        source = "1 x Good @ 1\n2 Bad @ 2\n3 x AlsoGood @ 3"
        self.assert_error_at(source, 2, 3, "expected 'x' after quantity")


if __name__ == "__main__":
    unittest.main()
