"""Summing line items into invoice totals.

An invoice parsed from this format can mix currencies line by line (a
consulting hour billed in EUR next to parts billed in USD), so a single
grand total would be meaningless. Instead the totals here are grouped
per currency code.
"""

from decimal import Decimal
from typing import Dict, List

from .models import LineItem


def totals_by_currency(items: List[LineItem]) -> Dict[str, Decimal]:
    """Sum each line item's total, grouped by currency code.

    Currencies with no line items do not appear in the result.
    """
    totals: Dict[str, Decimal] = {}
    for item in items:
        totals[item.currency] = totals.get(item.currency, Decimal(0)) + item.total
    return totals
