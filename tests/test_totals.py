import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from invoiceline import parse, totals_by_currency


class TotalsByCurrencyTests(unittest.TestCase):
    def test_groups_by_currency(self):
        source = "\n".join(
            [
                "3 x Widget bracket @ 12.50",
                "1 x On-site consulting hour @ 150 EUR discount 10%",
                "2 x Replacement cable @ 4.99 tax 8%",
            ]
        )
        items = parse(source)
        totals = totals_by_currency(items)
        # USD: 3 * 12.50 = 37.50, plus (2 * 4.99) + 8% tax = 10.7784
        # EUR: 150 minus 10% discount = 135.00
        self.assertEqual(
            totals,
            {
                "USD": Decimal("48.2784"),
                "EUR": Decimal("135.00"),
            },
        )

    def test_currency_with_no_items_is_absent(self):
        items = parse("1 x Widget @ 1 EUR")
        totals = totals_by_currency(items)
        self.assertNotIn("USD", totals)
        self.assertEqual(totals, {"EUR": Decimal("1")})

    def test_empty_list_gives_empty_totals(self):
        self.assertEqual(totals_by_currency([]), {})

    def test_single_currency_sums_all_lines(self):
        items = parse("1 x A @ 10\n2 x B @ 5")
        self.assertEqual(totals_by_currency(items), {"USD": Decimal("20")})


if __name__ == "__main__":
    unittest.main()
