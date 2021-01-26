from decimal import Decimal

from tests.base_test_case import BaseTestCase
from tradingbot.bo.strategy_bo import StrategyBO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.enums.action_enum import ActionEnum


class StrategyBOTestCase(BaseTestCase):

    def setUp(self):
        self.attempt = AttemptDTO(amount_buy=Decimal('1000'), distance_buy=Decimal('1'), delta_buy=Decimal('1.5'),
                                  amount_sell=Decimal('1000'), distance_sell=Decimal('1'), delta_sell=Decimal('1.5'))

    def test_counter_cyclical_buy(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('10'), Decimal('1')])
        action, number = StrategyBO.counter_cyclical(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.BUY)
        self.assertEqual(number, 1000)

    def test_counter_cyclical_sell(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('1'), Decimal('10')])
        action, number = StrategyBO.counter_cyclical(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.SELL)
        self.assertEqual(number, 100)

    def test_counter_cyclical_none(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('1'), Decimal('1')])
        action, number = StrategyBO.counter_cyclical(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.NONE)
        self.assertEqual(number, 0)

    def test_volume_trading_buy(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('10'), Decimal('1')])
        action, number = StrategyBO.volume_trading(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.BUY)
        self.assertEqual(number, 1000)

    def test_volume_trading_sell(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('1'), Decimal('10')])
        action, number = StrategyBO.volume_trading(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.SELL)
        self.assertEqual(number, 100)

    def test_volume_trading_none(self):
        intraday_list = self.create_intraday_list(decimal_list=[Decimal('1'), Decimal('1')])
        action, number = StrategyBO.volume_trading(intraday_list, intraday_list[1].date, self.attempt)
        self.assertEqual(action, ActionEnum.NONE)
        self.assertEqual(number, 0)
