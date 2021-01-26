from unittest.mock import patch

from tests.base_test_case import BaseTestCase
from tradingbot import db
from tradingbot.dao.portfolio_dao import PortfolioDAO
from tradingbot.dao.stock_dao import StockDAO
from tradingbot.entity.portfolio_entity import PortfolioEntity
from tradingbot.enums.mode_enum import ModeEnum


class PortfolioDAOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_read_all(self, isin):
        self.truncate_tables()
        isin.return_value = 'isin'
        StockDAO.update(('symbol1', 'symbol2', 'symbol3',))
        PortfolioDAO.create('symbol1', ModeEnum.FORWARD)
        PortfolioDAO.create('symbol2', ModeEnum.BACKWARD)
        portfolio = PortfolioDAO.read()
        self.assert_attributes(portfolio[0], symbol='symbol1', mode=ModeEnum.FORWARD, isin='isin')
        self.assert_attributes(portfolio[1], symbol='symbol2', mode=ModeEnum.BACKWARD, isin='isin')

    def test_read_filter_by_symbol(self):
        PortfolioDAO.update('symbol1', ModeEnum.BACKWARD)
        portfolio = PortfolioDAO.read_filter_by_symbol('symbol1')
        self.assertIsInstance(portfolio, PortfolioEntity)
        self.assert_attributes(portfolio, symbol='symbol1', mode=ModeEnum.BACKWARD)

    def test_update(self):
        PortfolioDAO.update('symbol1', ModeEnum.BACKWARD)
        portfolio = PortfolioDAO.read_filter_by_symbol('symbol1')
        self.assertIsInstance(portfolio, PortfolioEntity)
        self.assert_attributes(portfolio, symbol='symbol1', mode=ModeEnum.BACKWARD)

        PortfolioDAO.update('symbol3', ModeEnum.FORWARD)
        PortfolioDAO.update('symbol3', ModeEnum.BACKWARD)
        portfolio = PortfolioDAO.read_filter_by_symbol('symbol3')
        self.assertIsInstance(portfolio, PortfolioEntity)
        self.assert_attributes(portfolio, symbol='symbol3', mode=ModeEnum.BACKWARD)
