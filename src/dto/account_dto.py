from decimal import Decimal
from typing import Dict, NoReturn

from src.bo.inventory_bo import InventoryBO


class AccountDTO:

    def __init__(self, inventory: Dict[str, InventoryBO], cash: Decimal, total_value: Decimal,
                 total: Decimal) -> NoReturn:
        self.inventory: Dict[str, InventoryBO] = inventory
        self.cash: Decimal = cash
        self.total_value: Decimal = total_value
        self.total: Decimal = total
