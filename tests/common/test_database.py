from unittest.mock import patch, Mock

from tests.base_test_case import BaseTestCase
from tradingbot import db
from tradingbot.bo.configuration_bo import ConfigurationBO
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.common.database import Database
from tradingbot.enums.configuration_enum import ConfigurationEnum


class DatabaseTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    @patch('tradingbot.bo.portfolio_bo.tickers_sp500')
    @patch('tradingbot.bo.portfolio_bo.tickers_nasdaq')
    @patch('tradingbot.bo.stock_bo.get')
    def test_init(self, get, tickers_nasdaq, tickers_sp500):
        symbol_list = ('BBB', 'DDD', 'CCC', 'AAA')
        tickers_sp500.return_value = ('AAA', 'BBB')
        tickers_nasdaq.return_value = ('CCC', 'DDD')
        response = Mock()
        setattr(response, 'text', '"Stocks", "AAA|US0378331005|AAA||AAA", ')
        get.return_value = response
        Database.init()
        portfolio = PortfolioBO.forward_portfolio(100)
        self.assertEqual(len(portfolio), 4)
        for p, symbol in zip(portfolio, symbol_list):
            self.assertEqual(p, symbol)
        portfolio = PortfolioBO.backward_portfolio(100)
        self.assertEqual(len(portfolio), 4)
        for p, symbol in zip(portfolio, symbol_list):
            self.assertEqual(p, symbol)
        portfolio = PortfolioBO.backward_forward_portfolio()
        self.assertEqual(len(portfolio), 8)
        for p, symbol in zip(portfolio, symbol_list * 2):
            self.assertEqual(p, symbol)
        configurations = ConfigurationBO.read_all()
        for enum, configuration in zip(ConfigurationEnum.__iter__(), configurations):
            self.assert_attributes(configuration, identifier=enum.identifier, value=enum.val,
                                   description=enum.description)
