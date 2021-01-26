from decimal import Decimal
from unittest import TestCase

from tradingbot.bo.inventory_bo import InventoryBO


class InventoryBOTestCase(TestCase):
    def test_init(self):
        inventory = InventoryBO(Decimal('1'), Decimal('2'))
        self.assertEqual(inventory.number, Decimal('1'))
        self.assertEqual(inventory.price, Decimal('2'))

    def test_value(self):
        inventory = InventoryBO(Decimal('3'), Decimal('5'))
        self.assertEqual(inventory.value(), Decimal('15'))
