from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class LineItem:
    quantity: Decimal
    description: str
    unit_price: Decimal
    currency: str
    line: int
    discount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price

    @property
    def total(self) -> Decimal:
        amount = self.subtotal
        if self.discount is not None:
            amount -= amount * self.discount / 100
        if self.tax_rate is not None:
            amount += amount * self.tax_rate / 100
        return amount
