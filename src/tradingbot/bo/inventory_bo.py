from decimal import Decimal


class InventoryBO:

    def __init__(self, number: Decimal, price: Decimal) -> None:
        self.number = number
        self.price = price

    def value(self) -> Decimal:
        return self.number * self.price
