from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    quantity: Decimal
    description: str
    unit_price: Decimal
    currency: str
    line: int

    @property
    def total(self) -> Decimal:
        return self.quantity * self.unit_price
