from decimal import Decimal
from unittest import TestCase

from tradingbot.bo.broker_bo import BrokerBO
from tradingbot.bo.inventory_bo import InventoryBO
from tradingbot.common.constants import ZERO


class BrokerBOTestCase(TestCase):
    def test_update(self):
        broker = BrokerBO(cash=Decimal('10000'), fee=Decimal('3.9'))
        broker.update('AAA', Decimal('0.1'))
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.1'))
        broker.update('BBB', Decimal('0.2'))
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.1'))
        self.assertEqual(broker.inventory['BBB'].price, Decimal('0.2'))
        broker.update('AAA', Decimal('0.3'))
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.3'))
        self.assertEqual(broker.inventory['BBB'].price, Decimal('0.2'))
        broker.update('BBB', Decimal('0.4'))
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.3'))
        self.assertEqual(broker.inventory['BBB'].price, Decimal('0.4'))

    def test_buy(self):
        broker = BrokerBO(cash=Decimal('10000'), fee=Decimal('3.9'))
        buy = broker.buy('AAA', Decimal('0.1'), Decimal('10'))
        self.assertEqual(buy, True)
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.1'))
        self.assertEqual(broker.inventory['AAA'].number, Decimal('10'))
        self.assertEqual(broker.cash, Decimal('10000') - Decimal('1') - Decimal('3.9'))
        buy = broker.buy('AAA', Decimal('0.2'), Decimal('10'))
        self.assertEqual(buy, True)
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.2'))
        self.assertEqual(broker.inventory['AAA'].number, Decimal('20'))
        self.assertEqual(broker.cash, Decimal('10000') - Decimal('1') - Decimal('3.9') - Decimal('2') - Decimal('3.9'))

    def test_buy_insufficient_funds(self):
        broker = BrokerBO(cash=Decimal('10'), fee=Decimal('3.9'))
        buy = broker.buy('AAA', Decimal('10'), Decimal('10'))
        self.assertEqual(buy, False)

    def test_buy_number_zero(self):
        broker = BrokerBO(cash=Decimal('10000'), fee=Decimal('3.9'))
        buy = broker.buy('AAA', Decimal('10'), Decimal('0'))
        self.assertEqual(buy, False)

    def test_sell(self):
        broker = BrokerBO(cash=Decimal('10000'), fee=Decimal('3.9'))
        broker.inventory['AAA'] = InventoryBO(Decimal('20'), Decimal('0.1'))
        sell = broker.sell('AAA', Decimal('0.1'), Decimal('10'))
        self.assertEqual(sell, True)
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.1'))
        self.assertEqual(broker.inventory['AAA'].number, Decimal('10'))
        self.assertEqual(broker.cash, Decimal('10000') + Decimal('1') - Decimal('3.9'))
        sell = broker.sell('AAA', Decimal('0.2'), Decimal('10'))
        self.assertEqual(sell, True)
        self.assertEqual(broker.inventory['AAA'].price, Decimal('0.2'))
        self.assertEqual(broker.inventory['AAA'].number, ZERO)
        self.assertEqual(broker.cash, Decimal('10000') + Decimal('1') - Decimal('3.9') + Decimal('2') - Decimal('3.9'))

    def test_sell_insufficient_inventory(self):
        broker = BrokerBO(cash=Decimal('10'), fee=Decimal('3.9'))
        sell = broker.sell('AAA', Decimal('10'), Decimal('10'))
        self.assertEqual(sell, False)

    def test_sell_number_zero(self):
        broker = BrokerBO(cash=Decimal('10000'), fee=Decimal('3.9'))
        broker.inventory['AAA'] = InventoryBO(Decimal('20'), Decimal('0.1'))
        sell = broker.sell('AAA', Decimal('0.1'), Decimal('0'))
        self.assertEqual(sell, False)

    def test_funds(self):
        broker = BrokerBO(cash=Decimal('10'), fee=Decimal('3.9'))
        broker.inventory['AAA'] = InventoryBO(Decimal('10'), Decimal('0.1'))
        broker.inventory['BBB'] = InventoryBO(Decimal('20'), Decimal('0.2'))
        self.assertEqual(broker.funds(), Decimal('10') + Decimal('10') * Decimal('0.1') + Decimal('20') *
                         Decimal('0.2'))
